const { listItems } = require("../../utils/api");

// 首页逻辑
Page({
  data: {
    currentTab: 'lost',
    currentCategory: '全部',
    items: [],
    allItems: [],
    keyword: "",
    certOnly: false,
    selectedLocation: ""
  },

  // 页面加载
  onLoad(options) {
    console.log('首页加载');
    this.loadItemsList();
  },

  // 页面显示
  onShow() {
    console.log('首页显示');
  },

  // 加载物品列表
  loadItemsList() {
    wx.showLoading({
      title: '加载中...'
    });
    const itemType = this.data.currentTab === "lost" ? 1 : 2;
    const params = {
      item_type: itemType,
      page: 1,
      page_size: 50,
      keyword: this.data.keyword || ""
    };
    // 证件专搜或当前证件分类时，优先让后端按证件类检索
    if (this.data.certOnly || this.data.currentCategory === "证件") {
      params.item_type_id = 9;
    }
    listItems(params)
      .then((res) => {
        const note = res?.data?.note;
        if (note) {
          wx.showToast({ title: String(note).slice(0, 24), icon: "none" });
        }
        const raw = res?.data?.list || [];
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
        const mapped = raw.map((item) => ({
          id: item.id,
          type: item.item_type === 1 ? "lost" : "found",
          category: categoryMap[item.item_type_id] || "其他",
          title: item.title,
          coverImage: item.cover_image || "",
          statusLabel: item.status_label || "",
          certMatch: !!item.is_id_card_match,
          similarity: undefined,
          similarityText: "",
          location: item.location_name || "未知地点",
          date: (item.lost_found_time || "").slice(0, 10),
          user: "匿名用户",
          views: 0
        }));
        this.setData({ allItems: mapped });
        this.applyFilters();
      })
      .catch((err) => {
        wx.showToast({
          title: err?.message?.slice(0, 28) || "加载失败，请检查后端和IP",
          icon: "none"
        });
      })
      .finally(() => {
        wx.hideLoading();
      });
  },

  applyFilters() {
    const { allItems, currentCategory, selectedLocation } = this.data;
    const list = allItems.filter((item) => {
      const byCategory = currentCategory === "全部" || item.category === currentCategory;
      const byLocation = !selectedLocation || item.location === selectedLocation;
      return byCategory && byLocation;
    });
    this.setData({ items: list });
  },

  // 搜索输入
  onSearchInput(e) {
    this.setData({
      keyword: e.detail.value || ""
    });
  },

  // 搜索
  handleSearch() {
    this.loadItemsList();
    wx.showToast({
      title: "已筛选",
      icon: "none"
    });
  },

  clearFilters() {
    this.setData({
      keyword: "",
      selectedLocation: "",
      currentCategory: "全部",
      certOnly: false
    });
    this.loadItemsList();
    wx.showToast({
      title: "已取消筛选",
      icon: "none"
    });
  },

  goToSmartSearch() {
    wx.navigateTo({
      url: "/pages/smart-search/smart-search?scope=all"
    });
  },

  chooseFilterLocation() {
    wx.navigateTo({
      url: "/pages/location-picker/location-picker",
      success: (res) => {
        res.eventChannel.emit("initData", {
          selected: this.data.selectedLocation || "",
          pageTitle: "地点筛选",
        });
        res.eventChannel.on("locationSelected", ({ location }) => {
          const picked = location || "";
          const next = picked === this.data.selectedLocation ? "" : picked;
          this.setData({ selectedLocation: next });
          this.applyFilters();
          wx.showToast({ title: next ? `已按地点筛选：${next}` : "已清除地点筛选", icon: "none" });
        });
      },
    });
  },

  toggleCertOnly() {
    const next = !this.data.certOnly;
    this.setData({ certOnly: next });
    if (next && this.data.currentCategory !== "证件") {
      this.setData({ currentCategory: "证件" });
    }
    this.loadItemsList();
  },

  onImageError(e) {
    const id = e.currentTarget.dataset.id;
    const list = this.data.items.map((it) => {
      if (it.id === id) {
        return {
          ...it,
          coverImage: "/images/home.png"
        };
      }
      return it;
    });
    this.setData({ items: list });
  },

  // 切换标签
  switchTab(e) {
    const type = e.currentTarget.dataset.type;
    this.setData({
      currentTab: type
    });
    this.loadItemsList();
  },

  // 切换分类
  switchCategory(e) {
    const category = e.currentTarget.dataset.category;
    this.setData({
      currentCategory: category,
      certOnly: category === "证件"
    });
    // 分类切换后直接走一次后端筛选，确保逻辑和展示一致
    this.loadItemsList();
  },

  // 物品点击
  handleItemClick(e) {
    const itemId = e.currentTarget.dataset.id;
    wx.navigateTo({
      url: `/pages/item-detail/item-detail?id=${itemId}`
    });
  },

  // 首页加号已移除，保留发布入口在 TabBar
});