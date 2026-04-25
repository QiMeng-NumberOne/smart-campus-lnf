const { me, updateProfile } = require("../../../utils/api");

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
    Promise.all([me()]).then(([res]) => {
      const data = res?.data || {};
      const savedSettings = wx.getStorageSync('notificationSettings') || {};
      this.setData({
        settings: {
          ...this.data.settings,
          ...savedSettings,
          matchNotification: !!data.match_notification_enabled
        }
      });
    }).catch(() => {
      const savedSettings = wx.getStorageSync('notificationSettings');
      if (savedSettings) {
        this.setData({ settings: savedSettings });
      }
    });
  },

  // 返回
  goBack() {
    wx.navigateBack();
  },

  // 设置变更
  async onSettingChange(e) {
    const key = e.currentTarget.dataset.key;
    const value = !!e.detail.value;

    if (key === "matchNotification" && value) {
      // 开启匹配通知时，申请微信订阅消息权限
      const tmplId = getApp()?.globalData?.wechatMatchTemplateId || "";
      if (!tmplId) {
        wx.showToast({ title: "请先配置订阅模板ID", icon: "none" });
        return;
      }
      try {
        await new Promise((resolve, reject) => {
          wx.requestSubscribeMessage({
            tmplIds: [tmplId],
            success: resolve,
            fail: reject
          });
        });
      } catch (_) {
        wx.showToast({ title: "未授予订阅权限", icon: "none" });
        return;
      }
    }

    const newSettings = {
      ...this.data.settings,
      [key]: value
    };

    this.setData({
      settings: newSettings
    });

    // 保存设置
    wx.setStorageSync('notificationSettings', newSettings);
    if (key === "matchNotification") {
      updateProfile({ match_notification_enabled: value }).catch(() => {
        wx.showToast({ title: "同步服务器失败", icon: "none" });
      });
    }
    console.log('设置已保存:', newSettings);
  }
});