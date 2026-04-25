const { myItems } = require("../../utils/api");

Page({
  data: {
    list: [],
    page: 1,
    pageSize: 20,
    itemType: null,
    pageTitle: "我的发布",
    status: null
  },

  onLoad(options) {
    const type = Number(options?.itemType || 0) || null;
    const status = Number(options?.status || 0) || null;
    let title = type === 1 ? "我的寻物" : type === 2 ? "我的招领" : "我的发布";
    if (type === 1 && status === 2) title = "已找回记录";
    this.setData({
      itemType: type,
      pageTitle: title,
      status
    });
    wx.setNavigationBarTitle({ title });
  },

  onShow() {
    this.loadData();
  },

  loadData() {
    wx.showLoading({ title: "加载中..." });
    myItems({
      page: this.data.page,
      page_size: this.data.pageSize,
      item_type: this.data.itemType || undefined,
      status: this.data.status || undefined
    })
      .then((res) => {
        const list = (res?.data?.list || []).map((item) => ({
          ...item,
          typeText: item.item_type === 1 ? "寻物" : "招领",
          timeText: item.lost_found_time || item.created_at || "",
          locationText: item.location_detail || item.location_name || "地点未填写",
          coverImage: item.cover_image || item.coverImage || "/images/home.png"
        }));
        this.setData({ list });
      })
      .catch(() => wx.showToast({ title: "加载失败", icon: "none" }))
      .finally(() => wx.hideLoading());
  },

  goDetail(e) {
    const id = e.currentTarget.dataset.id;
    wx.navigateTo({ url: `/pages/item-detail/item-detail?id=${id}` });
  },

  onImageError(e) {
    const id = e.currentTarget.dataset.id;
    const list = this.data.list.map((it) => (
      it.id === id ? { ...it, coverImage: "/images/home.png" } : it
    ));
    this.setData({ list });
  },
});
