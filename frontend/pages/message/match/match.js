const { listMessages, markMessageRead } = require("../../../utils/api");

Page({
  data: {
    matchNotifications: []
  },

  loadMatchMessages(markRead = false) {
    listMessages({ page: 1, page_size: 100 })
      .then((res) => {
        const rows = res?.data?.list || [];
        const matchRows = rows.filter((x) => x.kind === "match");
        const matches = matchRows
          .map((x) => ({
            id: x.id,
            itemId: x.target_item_id || x.item_id,
            title: "物品匹配成功",
            content: x.content || "检测到与您帖子高度相似的招领/寻物信息。",
            time: x.created_at || "",
            isRead: !!x.is_read
          }));
        this.setData({ matchNotifications: matches });
        if (markRead) {
          const unreadIds = matchRows.filter((m) => !m.is_read).map((m) => m.id);
          if (unreadIds.length) {
            Promise.all(unreadIds.map((id) => markMessageRead(id))).catch(() => {});
          }
        }
      })
      .catch(() => this.setData({ matchNotifications: [] }));
  },

  onLoad() {
    this.loadMatchMessages(true);
  },

  onShow() {
    this.loadMatchMessages(true);
  },

  goBack() {
    wx.navigateBack();
  },

  openMatchDetail(e) {
    const itemId = Number(e.currentTarget.dataset.itemId);
    const messageId = Number(e.currentTarget.dataset.messageId);
    if (messageId) {
      markMessageRead(messageId).catch(() => {});
    }
    if (!itemId) return;
    wx.navigateTo({ url: `/pages/item-detail/item-detail?id=${itemId}` });
  }
});