Page({
  data: {
    systemNotifications: [
      {
        id: 1,
        title: '系统维护通知',
        content: '系统将于今晚23:00-次日凌晨2:00进行维护，期间部分功能可能暂时不可用。',
        time: '2026-04-13 09:00'
      },
      {
        id: 2,
        title: '新功能上线',
        content: '失物招领小程序新增物品智能匹配功能，快来体验吧！',
        time: '2026-04-10 14:30'
      },
      {
        id: 3,
        title: '安全提醒',
        content: '请不要在平台上泄露个人敏感信息，谨防诈骗。',
        time: '2026-04-05 10:00'
      }
    ]
  },
  onLoad: function() {
    console.log('系统通知页面加载');
  },
  onShow: function() {
    console.log('系统通知页面显示');
  },
  goBack: function() {
    wx.navigateBack();
  }
});