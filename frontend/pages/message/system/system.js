const { listMessages, markMessageRead } = require("../../../utils/api");

Page({
  data: {
    systemNotifications: []
  },
  onLoad: function() {
    this.loadMessages();
  },
  onShow: function() {
    this.loadMessages();
  },
  loadMessages() {
    listMessages({ page: 1, page_size: 50 })
      .then((res) => {
        const list = res?.data?.list || [];
        this.setData({
          systemNotifications: list.map((i) => ({
            id: i.id,
            title: i.is_read ? "系统消息" : "未读消息",
            content: i.content,
            time: i.created_at
          }))
        });
      })
      .catch(() => this.setData({ systemNotifications: [] }));
  },
  openMsg(e) {
    const id = e.currentTarget.dataset.id;
    markMessageRead(id).finally(() => this.loadMessages());
  },
  goBack: function() {
    wx.navigateBack();
  }
});