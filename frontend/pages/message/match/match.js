Page({
  data: {
    matchNotifications: [
      {
        id: 1,
        title: '物品匹配成功',
        content: '您发布的寻物启事与一条失物招领信息匹配度较高，点击查看详情。',
        time: '2026-04-13 10:30'
      },
      {
        id: 2,
        title: '物品匹配成功',
        content: '您发布的失物招领信息与一条寻物启事匹配度较高，点击查看详情。',
        time: '2026-04-12 15:45'
      }
    ]
  },
  onLoad: function() {
    console.log('匹配通知页面加载');
  },
  onShow: function() {
    console.log('匹配通知页面显示');
  },
  goBack: function() {
    wx.navigateBack();
  }
});