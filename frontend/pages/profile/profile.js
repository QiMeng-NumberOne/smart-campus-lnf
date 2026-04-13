// 个人中心页面逻辑
Page({
  data: {
    user: {
      id: 1,
      name: '李同学',
      avatar: '',
      school: '计算机学院',
      grade: '2022级本科',
      isVerified: true,
      isStudent: true,
      stats: {
        lostCount: 3,
        foundCount: 2,
        claimCount: 1,
        likes: 47
      },
      level: {
        name: '校园好市民',
        level: 3,
        credit: 320,
        nextCredit: 400
      }
    }
  },

  // 页面加载
  onLoad(options) {
    console.log('个人中心页面加载');
    this.loadUserProfile();
  },

  // 加载用户信息
  loadUserProfile() {
    wx.showLoading({
      title: '加载中...'
    });

    // 模拟API请求
    setTimeout(() => {
      wx.hideLoading();
      // 这里可以从API获取用户信息
    }, 500);
  },

  // 跳转到我的寻物
  goToMyLost() {
    wx.showToast({
      title: '查看我的寻物',
      icon: 'none'
    });
  },

  // 跳转到我的招领
  goToMyClaim() {
    wx.showToast({
      title: '查看我的招领',
      icon: 'none'
    });
  },

  // 跳转到已找回记录
  goToFoundRecords() {
    wx.showToast({
      title: '查看已找回记录',
      icon: 'none'
    });
  },

  // 跳转到AI匹配记录
  goToAiMatch() {
    wx.showToast({
      title: '查看AI匹配记录',
      icon: 'none'
    });
  },

  // 跳转到消息通知
  goToNotification() {
    wx.navigateTo({
      url: '/pages/message/message'
    });
  }
});