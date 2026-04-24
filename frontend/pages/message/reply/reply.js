const { listMessages, markMessageRead } = require("../../../utils/api");

Page({
  data: {
    replyNotifications: []
  },
  onLoad: function() {
    this.loadData();
  },
  onShow: function() {
    this.loadData();
  },
  loadData() {
    listMessages({ page: 1, page_size: 50 })
      .then((res) => {
        const list = res?.data?.list || [];
        const replies = list
          .filter((m) => m.kind === "comment")
          .map((m) => ({
            id: m.id,
            itemId: m.item_id,
            title: "有人评论了你的物品",
            content: m.reply_to_username ? `回复 ${m.reply_to_username}：${m.content}` : m.content,
            time: m.created_at
          }));
        this.setData({ replyNotifications: replies });
      })
      .catch(() => this.setData({ replyNotifications: [] }));
  },
  openReply(e) {
    const id = e.currentTarget.dataset.id;
    const itemId = e.currentTarget.dataset.itemId;
    markMessageRead(id).finally(() => {
      this.loadData();
      wx.navigateTo({
        url: `/pages/item-detail/item-detail?id=${itemId}&commentId=${id}`
      });
    });
  },
  goBack: function() {
    wx.navigateBack();
  }
});