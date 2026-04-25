const { listMessages, markMessageRead } = require("../../../utils/api");

Page({
  data: {
    systemNotifications: []
  },
  onLoad: function () {
    this.loadMessages(true);
  },
  onShow: function () {
    this.loadMessages(true);
  },
  loadMessages(markRead = false) {
    listMessages({ page: 1, page_size: 50 })
      .then((res) => {
        const list = res?.data?.list || [];
        const systems = list.filter((i) => i.kind === "system_reminder");
        this.setData({
          systemNotifications: systems.map((i) => ({
            id: i.id,
            title: "系统通知",
            content: i.content,
            time: i.created_at
          }))
        });
        if (markRead) {
          const unreadIds = systems.filter((i) => !i.is_read).map((i) => i.id);
          if (unreadIds.length) {
            Promise.all(unreadIds.map((id) => markMessageRead(id))).catch(() => {});
          }
        }
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