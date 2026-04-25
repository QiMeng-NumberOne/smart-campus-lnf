const {
  getItemDetail,
  addFavorite,
  removeFavorite,
  listComments,
  createComment,
  updateItemStatus,
  listRelatedItems,
  recordRecommendEvent
} = require("../../utils/api");

Page({
  data: {
    itemId: null,
    commentId: null,
    item: null,
    isFavorite: false,
    comments: [],
    commentInput: "",
    commentOrder: "desc",
    replyToCommentId: null,
    replyToUsername: "",
    isOwner: false,
    statusActions: [],
    relatedItems: [],
    relatedNote: ""
  },

  onLoad(options) {
    this.setData({
      itemId: options.id,
      commentId: options.commentId ? Number(options.commentId) : null
    });
    this.loadDetail();
  },

  loadDetail() {
    wx.showLoading({ title: "加载中..." });
    getItemDetail(this.data.itemId)
      .then((res) => {
        const detail = res?.data || null;
        const userInfo = wx.getStorageSync("userInfo") || {};
        const isOwner = !!detail && Number(detail.user_id) === Number(userInfo.id || userInfo.user_id);
        const statusActions = this.buildStatusActions(detail);
        this.setData({
          item: detail,
          isOwner,
          statusActions
        });
        this.loadComments();
        this.loadRelated();
      })
      .catch(() => {
        wx.showToast({ title: "详情加载失败", icon: "none" });
      })
      .finally(() => wx.hideLoading());
  },

  buildStatusActions(item) {
    if (!item) return [];
    const labels = item.item_type === 1
      ? { resolved: "标记已找回", unresolved: "改回未找回", closed: "关闭帖子" }
      : { resolved: "标记已认领", unresolved: "改回未认领", closed: "关闭帖子" };
    if (item.status === 1) {
      return [{ status: 2, text: labels.resolved }, { status: 3, text: labels.closed }];
    }
    if (item.status === 2) {
      return [{ status: 1, text: labels.unresolved }, { status: 3, text: labels.closed }];
    }
    return [{ status: 1, text: labels.unresolved }];
  },

  changeItemStatus(e) {
    const status = Number(e.currentTarget.dataset.status);
    if (!status) return;
    updateItemStatus(this.data.itemId, { status })
      .then(() => {
        wx.showToast({ title: "状态已更新", icon: "none" });
        this.loadDetail();
      })
      .catch((err) => {
        wx.showToast({ title: err?.message?.slice(0, 20) || "更新失败", icon: "none" });
      });
  },

  loadComments() {
    listComments(this.data.itemId, { order: this.data.commentOrder })
      .then((res) => {
        this.setData({
          comments: res?.data?.list || []
        });
        if (this.data.commentId) {
          setTimeout(() => {
            wx.pageScrollTo({
              selector: `#comment-${this.data.commentId}`,
              duration: 250
            });
          }, 100);
        }
      })
      .catch(() => {
        this.setData({ comments: [] });
      });
  },

  toggleFavorite() {
    const action = this.data.isFavorite ? removeFavorite : addFavorite;
    action(this.data.itemId)
      .then(() => {
        const next = !this.data.isFavorite;
        this.setData({ isFavorite: next });
        wx.showToast({ title: next ? "已收藏" : "已取消", icon: "none" });
      })
      .catch(() => wx.showToast({ title: "操作失败", icon: "none" }));
  },

  loadRelated() {
    const id = this.data.itemId;
    if (!id) return;
    listRelatedItems(id, { limit: 8 })
      .then((res) => {
        const data = res?.data || {};
        this.setData({
          relatedItems: data.list || [],
          relatedNote: data.note || ""
        });
      })
      .catch(() => this.setData({ relatedItems: [], relatedNote: "" }));
  },

  openRelated(e) {
    const id = e.currentTarget.dataset.id;
    if (!id) return;
    wx.navigateTo({ url: `/pages/item-detail/item-detail?id=${id}` });
  },

  callContact() {
    const contact = this.data.item?.contact_info;
    if (!contact) {
      wx.showToast({ title: "暂无联系方式", icon: "none" });
      return;
    }
    const itemId = this.data.itemId;
    if (itemId) {
      recordRecommendEvent({ item_id: Number(itemId), behavior_type: "click_contact" }).catch(() => {});
    }
    wx.setClipboardData({
      data: contact,
      success: () => wx.showToast({ title: "联系方式已复制", icon: "none" })
    });
  },

  previewItemImage(e) {
    const index = Number(e.currentTarget.dataset.index || 0);
    const images = (this.data.item?.images || []).map((img) => img.url).filter(Boolean);
    if (!images.length) return;
    wx.previewImage({
      current: images[index] || images[0],
      urls: images
    });
  },

  onCommentInput(e) {
    this.setData({ commentInput: e.detail.value || "" });
  },

  toggleCommentOrder() {
    const next = this.data.commentOrder === "desc" ? "asc" : "desc";
    this.setData({ commentOrder: next });
    this.loadComments();
  },

  startReply(e) {
    const commentId = Number(e.currentTarget.dataset.commentId);
    const username = e.currentTarget.dataset.username || "";
    this.setData({
      replyToCommentId: commentId,
      replyToUsername: username,
      commentInput: `@${username} `
    });
  },

  clearReplyTarget() {
    this.setData({
      replyToCommentId: null,
      replyToUsername: "",
      commentInput: ""
    });
  },

  submitComment() {
    const token = wx.getStorageSync("token");
    if (!token) {
      wx.showToast({ title: "请先登录", icon: "none" });
      return;
    }
    const content = (this.data.commentInput || "").trim();
    if (!content) {
      wx.showToast({ title: "请输入评论内容", icon: "none" });
      return;
    }
    createComment(this.data.itemId, {
      content,
      reply_to_comment_id: this.data.replyToCommentId,
      reply_to_username: this.data.replyToUsername || null
    })
      .then(() => {
        this.setData({
          commentInput: "",
          replyToCommentId: null,
          replyToUsername: ""
        });
        wx.showToast({ title: "评论成功", icon: "none" });
        this.loadComments();
      })
      .catch((err) => {
        wx.showToast({ title: err?.message?.slice(0, 20) || "评论失败", icon: "none" });
      });
  }
});
