const { LOCATION_GROUPS, ALL_LOCATIONS } = require("../../utils/campus-locations");

Page({
  data: {
    pageTitle: "选择地点",
    selected: "",
    keyword: "",
    groups: LOCATION_GROUPS,
    filteredGroups: LOCATION_GROUPS,
  },

  onLoad() {
    const channel = this.getOpenerEventChannel?.();
    if (channel) {
      channel.on("initData", (payload = {}) => {
        this.setData({
          selected: payload.selected || "",
          pageTitle: payload.pageTitle || "选择地点",
        });
        wx.setNavigationBarTitle({ title: payload.pageTitle || "选择地点" });
      });
    }
  },

  onKeywordInput(e) {
    const keyword = (e.detail.value || "").trim();
    if (!keyword) {
      this.setData({ keyword, filteredGroups: this.data.groups });
      return;
    }
    const lower = keyword.toLowerCase();
    const filtered = this.data.groups
      .map((g) => ({
        ...g,
        options: g.options.filter((opt) => opt.toLowerCase().includes(lower)),
      }))
      .filter((g) => g.options.length > 0);
    this.setData({ keyword, filteredGroups: filtered });
  },

  quickPick(e) {
    const idx = Number(e.currentTarget.dataset.index || 0);
    const location = ALL_LOCATIONS[idx] || "";
    if (!location) return;
    this.submitLocation(location);
  },

  selectLocation(e) {
    const location = e.currentTarget.dataset.location || "";
    if (!location) return;
    this.submitLocation(location);
  },

  submitLocation(location) {
    const channel = this.getOpenerEventChannel?.();
    if (channel) {
      channel.emit("locationSelected", { location });
    }
    wx.navigateBack();
  },
});
