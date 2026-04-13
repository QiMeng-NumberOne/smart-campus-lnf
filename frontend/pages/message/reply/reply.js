Page({
  data: {
    replyNotifications: [
      {
        id: 1,
        title: '有人回复了您的寻物启事',
        content: '用户"小明"回复了您发布的寻物启事："我看到了您的钱包，请问在哪里可以联系您？"',
        time: '2026-04-13 11:20'
      },
      {
        id: 2,
        title: '有人回复了您的失物招领',
        content: '用户"小红"回复了您发布的失物招领："这是我的笔记本，谢谢您！"',
        time: '2026-04-12 16:30'
      }
    ]
  },
  onLoad: function() {
    console.log('回复通知页面加载');
  },
  onShow: function() {
    console.log('回复通知页面显示');
  },
  goBack: function() {
    wx.navigateBack();
  }
});