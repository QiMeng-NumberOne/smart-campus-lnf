const { me, myItems, listFavorites, unreadCount } = require("../../utils/api");

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
  },

  onShow() {
    this.loadUserProfile();
  },

  // 加载用户信息
  loadUserProfile() {
    wx.showLoading({
      title: '加载中...'
    });
    Promise.all([me(), myItems(), listFavorites(), unreadCount()])
      .then(([u, mine, favs, unread]) => {
        const mineList = mine?.data?.list || [];
        const lostCount = mineList.filter((i) => i.item_type === 1).length;
        const claimCount = mineList.filter((i) => i.item_type === 2).length;
        this.setData({
          "user.name": u?.data?.username || "未登录",
          "user.avatar": u?.data?.avatar || "",
          "user.school": u?.data?.college || "未填写学院",
          "user.grade": u?.data?.grade || "未填写年级",
          "user.stats.lostCount": lostCount,
          "user.stats.claimCount": claimCount,
          "user.stats.likes": favs?.data?.total || 0,
          "user.stats.foundCount": unread?.data?.count || 0
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
    wx.navigateTo({ url: "/pages/message/system/system" });
  },

  // 跳转到AI匹配记录
  goToAiMatch() {
    wx.navigateTo({ url: "/pages/message/match/match" });
  },

  // 跳转到消息通知
  goToNotification() {
    wx.navigateTo({
      url: '/pages/message/message'
    });
  }
});