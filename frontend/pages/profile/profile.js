const { me, meStats } = require("../../utils/api");

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
        likes: 47,
        lostOngoingCount: 0,
        claimOngoingCount: 0
      },
      level: {
        name: '校园好市民',
        level: 3,
        credit: 320,
        nextCredit: 400
      }
    }
  },

  calcLevel(stats = {}) {
    const credit =
      (Number(stats.lost_count || 0) * 8) +
      (Number(stats.claim_count || 0) * 10) +
      (Number(stats.found_count || 0) * 30) +
      (Number(stats.likes_received || 0) * 2);
    const level = Math.max(1, Math.floor(credit / 120) + 1);
    const nextCredit = level * 120;
    const titleMap = {
      1: "新手市民",
      2: "热心同学",
      3: "校园好市民",
      4: "诚信先锋",
      5: "失物守护者",
    };
    return {
      credit,
      level,
      nextCredit,
      name: titleMap[Math.min(level, 5)] || "校园好市民",
    };
  },

  // 页面加载
  onLoad(options) {
    console.log('个人中心页面加载');
  },

  onShow() {
    this.loadUserProfile();
  },

  // 加载用户信息
  loadUserProfile() {
    wx.showLoading({
      title: '加载中...'
    });
    Promise.all([me(), meStats()])
      .then(([u, statsResp]) => {
        const stats = statsResp?.data || {};
        const level = this.calcLevel(stats);
        this.setData({
          "user.name": u?.data?.username || "未登录",
          "user.avatar": u?.data?.avatar || "",
          "user.school": u?.data?.college || "未填写学院",
          "user.grade": u?.data?.grade || "未填写年级",
          "user.stats.lostCount": stats.lost_count || 0,
          "user.stats.claimCount": stats.claim_count || 0,
          "user.stats.likes": stats.likes_received || 0,
          "user.stats.foundCount": stats.found_count || 0,
          "user.stats.lostOngoingCount": stats.lost_ongoing_count || 0,
          "user.stats.claimOngoingCount": stats.claim_ongoing_count || 0,
          "user.level.credit": level.credit,
          "user.level.level": level.level,
          "user.level.nextCredit": level.nextCredit,
          "user.level.name": level.name
        });
      })
      .catch(() => {
        wx.showToast({ title: "用户信息加载失败", icon: "none" });
      })
      .finally(() => wx.hideLoading());
  },

  goEditProfile() {
    wx.navigateTo({ url: "/pages/profile-edit/profile-edit" });
  },

  // 跳转到我的寻物
  goToMyLost() {
    wx.navigateTo({ url: "/pages/my-items/my-items?itemType=1" });
  },

  // 跳转到我的招领
  goToMyClaim() {
    wx.navigateTo({ url: "/pages/my-items/my-items?itemType=2" });
  },

  // 跳转到已找回记录
  goToFoundRecords() {
    wx.navigateTo({ url: "/pages/my-items/my-items?itemType=1&status=2" });
  },

  handleLogout() {
    wx.showModal({
      title: "退出登录",
      content: "确认退出当前账号吗？",
      confirmText: "退出",
      confirmColor: "#ef4444",
      success: (res) => {
        if (!res.confirm) return;
        wx.removeStorageSync("token");
        wx.removeStorageSync("userInfo");
        wx.reLaunch({
          url: "/pages/login/login",
        });
      },
    });
  },

  
});