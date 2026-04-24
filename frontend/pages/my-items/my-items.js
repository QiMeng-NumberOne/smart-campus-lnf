const { myItems } = require("../../utils/api");

Page({
  data: {
    list: [],
    page: 1,
    pageSize: 20,
    itemType: null,
    pageTitle: "我的发布"
  },

  onLoad(options) {
    const type = Number(options?.itemType || 0) || null;
    const title = type === 1 ? "我的寻物" : type === 2 ? "我的招领" : "我的发布";
    this.setData({
      itemType: type,
      pageTitle: title
    });
    wx.setNavigationBarTitle({ title });
  },

  onShow() {
    this.loadData();
  },

  loadData() {
    wx.showLoading({ title: "加载中..." });
    myItems({ page: this.data.page, page_size: this.data.pageSize, item_type: this.data.itemType || undefined })
      .then((res) => {
        this.setData({ list: res?.data?.list || [] });
      })
      .catch(() => wx.showToast({ title: "加载失败", icon: "none" }))
      .finally(() => wx.hideLoading());
  },

  goDetail(e) {
    const id = e.currentTarget.dataset.id;
    wx.navigateTo({ url: `/pages/item-detail/item-detail?id=${id}` });
  }
});
