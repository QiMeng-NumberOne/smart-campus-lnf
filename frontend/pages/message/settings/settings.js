// 消息设置页面逻辑
Page({
  data: {
    settings: {
      systemNotification: true,
      matchNotification: true,
      replyNotification: true,
      soundRemind: true,
      vibrationRemind: false
    }
  },

  // 页面加载
  onLoad(options) {
    console.log('消息设置页面加载');
    this.loadSettings();
  },

  // 加载设置
  loadSettings() {
    // 这里可以从本地存储或API获取设置
    const savedSettings = wx.getStorageSync('notificationSettings');
    if (savedSettings) {
      this.setData({
        settings: savedSettings
      });
    }
  },

  // 返回
  goBack() {
    wx.navigateBack();
  },

  // 设置变更
  onSettingChange(e) {
    const key = e.currentTarget.dataset.key;
    const value = e.detail.value[0] ? true : false;
    
    const newSettings = {
      ...this.data.settings,
      [key]: value
    };
    
    this.setData({
      settings: newSettings
    });
    
    // 保存设置
    wx.setStorageSync('notificationSettings', newSettings);
    console.log('设置已保存:', newSettings);
  }
});