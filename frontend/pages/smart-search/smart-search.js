const { searchByText, searchByImage } = require("../../utils/api");

function mapCategory(itemTypeId) {
  const categoryMap = {
    1: "电子设备",
    2: "电子设备",
    3: "其他",
    4: "电子设备",
    5: "证件",
    6: "其他",
    7: "服装",
    8: "电子设备",
    9: "证件",
    10: "其他"
  };
  return categoryMap[itemTypeId] || "其他";
}

function mapItem(item) {
  return {
    id: item.id,
    type: item.item_type === 1 ? "lost" : "found",
    category: mapCategory(item.item_type_id),
    title: item.title,
    coverImage: item.cover_image || "",
    statusLabel: item.status_label || "",
    similarity: item.similarity,
    similarityText: item.similarity !== undefined ? `${Math.round(Number(item.similarity || 0) * 100)}%` : "",
    location: item.location_name || "未知地点",
    date: (item.lost_found_time || "").slice(0, 10),
    user: "匿名用户"
  };
}

Page({
  data: {
    keyword: "",
    scopeAll: false,
    itemType: null,
    itemTypeId: null,
    itemTypeFilter: "all",
    mode: "text",
    rawResults: [],
    results: []
  },

  onLoad(options) {
    if (options?.scope === "all") {
      this.setData({ scopeAll: true, itemType: null, itemTypeId: null, itemTypeFilter: "all" });
      return;
    }
    const itemType = options?.item_type ? Number(options.item_type) : null;
    const itemTypeId = options?.item_type_id ? Number(options.item_type_id) : null;
    this.setData({ scopeAll: false, itemType, itemTypeId, itemTypeFilter: "all" });
  },

  switchItemTypeFilter(e) {
    const filter = e.currentTarget.dataset.filter;
    const itemType = filter === "lost" ? 1 : filter === "found" ? 2 : null;
    this.setData({ itemTypeFilter: filter, itemType }, () => this.applyCurrentFilter());
  },

  applyCurrentFilter() {
    const filter = this.data.itemTypeFilter;
    const src = this.data.rawResults || [];
    if (filter === "lost") {
      this.setData({ results: src.filter((it) => it.type === "lost") });
      return;
    }
    if (filter === "found") {
      this.setData({ results: src.filter((it) => it.type === "found") });
      return;
    }
    this.setData({ results: src });
  },

  switchMode(e) {
    this.setData({ mode: e.currentTarget.dataset.mode });
  },

  onKeywordInput(e) {
    this.setData({ keyword: e.detail.value || "" });
  },

  runTextSearch() {
    const keyword = (this.data.keyword || "").trim();
    if (!keyword) {
      wx.showToast({ title: "请输入关键词", icon: "none" });
      return;
    }
    try {
      wx.hideLoading();
    } catch (e) {
      /* ignore */
    }
    wx.showLoading({ title: "文搜中..." });
    const params = { keyword, top_k: 50 };
    if (this.data.itemType != null) params.item_type = this.data.itemType;
    if (this.data.itemTypeId) params.item_type_id = this.data.itemTypeId;
    searchByText(params)
      .then((res) => {
        const list = res?.data?.list || [];
        this.setData({ rawResults: list.map(mapItem) }, () => this.applyCurrentFilter());
        if (!list.length) wx.showToast({ title: "未找到匹配结果", icon: "none" });
      })
      .catch((err) => {
        wx.showToast({ title: err?.message?.slice(0, 26) || "文搜失败", icon: "none" });
      })
      .finally(() => wx.hideLoading());
  },

  runImageSearch() {
    wx.chooseImage({
      count: 1,
      sizeType: ["compressed"],
      sourceType: ["album", "camera"],
      success: (res) => {
        const filePath = res.tempFilePaths?.[0];
        if (!filePath) return;
        try {
          wx.hideLoading();
        } catch (e) {
          /* ignore */
        }
        wx.showLoading({ title: "图搜中..." });
        const formData = { top_k: 50 };
        if (this.data.itemType != null) formData.item_type = this.data.itemType;
        if (this.data.itemTypeId) formData.item_type_id = this.data.itemTypeId;
        searchByImage(filePath, formData)
          .then((result) => {
            const list = result?.data?.list || [];
            this.setData({ rawResults: list.map(mapItem) }, () => this.applyCurrentFilter());
            if (!list.length) wx.showToast({ title: "未找到相似物品", icon: "none" });
          })
          .catch((err) => {
            wx.showToast({ title: err?.message?.slice(0, 26) || "图搜失败", icon: "none" });
          })
          .finally(() => wx.hideLoading());
      }
    });
  },

  handleRun() {
    if (this.data.mode === "text") {
      this.runTextSearch();
      return;
    }
    this.runImageSearch();
  },

  onImageError(e) {
    const id = e.currentTarget.dataset.id;
    const next = this.data.results.map((it) => (it.id === id ? { ...it, coverImage: "/images/home.png" } : it));
    this.setData({ results: next });
  },

  handleItemClick(e) {
    const itemId = e.currentTarget.dataset.id;
    wx.navigateTo({ url: `/pages/item-detail/item-detail?id=${itemId}` });
  }
});
