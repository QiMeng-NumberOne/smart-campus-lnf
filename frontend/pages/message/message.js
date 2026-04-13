// 消息页面逻辑
Page({
  data: {
    // 消息数据
  },

  // 页面加载
  onLoad(options) {
    console.log('消息页面加载');
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