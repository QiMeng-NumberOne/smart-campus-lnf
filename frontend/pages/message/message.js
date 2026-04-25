const { listMessages } = require("../../utils/api");

// 消息页面逻辑
Page({
  data: {
    unread: 0,
    systemUnread: 0,
    matchUnread: 0,
    replyUnread: 0
  },

  // 页面加载
  onLoad(options) {
    this.loadSummary();
  },

  onShow() {
    this.loadSummary();
  },

  loadSummary() {
    listMessages({ page: 1, page_size: 200 })
      .then((res) => {
        const list = res?.data?.list || [];
        let unread = 0;
        let systemUnread = 0;
        let matchUnread = 0;
        let replyUnread = 0;
        list.forEach((msg) => {
          if (!msg?.is_read) {
            unread += 1;
            if (msg.kind === "match") {
              matchUnread += 1;
            } else if (msg.kind === "comment") {
              replyUnread += 1;
            } else if (msg.kind === "system_reminder") {
              systemUnread += 1;
            }
          }
        });
        this.setData({ unread, systemUnread, matchUnread, replyUnread });
      })
      .catch(() => this.setData({ unread: 0, systemUnread: 0, matchUnread: 0, replyUnread: 0 }));
  },

  // 返回
  goBack() {
    wx.navigateBack();
  },

  // 跳转到系统通知页面
  goToSystemNotification() {
    wx.navigateTo({
      url: '/pages/message/system/system'
    });
  },

  // 跳转到匹配通知页面
  goToMatchNotification() {
    wx.navigateTo({
      url: '/pages/message/match/match'
    });
  },

  // 跳转到回复通知页面
  goToReplyNotification() {
    wx.navigateTo({
      url: '/pages/message/reply/reply'
    });
  },

  // 跳转到消息设置页面
  goToMessageSettings() {
    wx.navigateTo({
      url: '/pages/message/settings/settings'
    });
  }
});