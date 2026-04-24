const { me, updateProfile } = require("../../utils/api");

const currentYear = new Date().getFullYear();
const gradeOptions = [];
for (let y = currentYear; y >= 2010; y--) {
  gradeOptions.push(`${y}`);
}

const collegeOptions = [
  "文学院", "外国语学院", "历史文化学院 民族学院", "国际学院", "汉语言文献研究所",
  "中国新诗研究所", "马克思主义学院", "经济管理学院", "数学与统计学院", "电子信息工程学院",
  "人工智能学院", "化学化工学院", "材料与能源学院", "资源环境学院", "地理科学学院",
  "工程技术学院", "食品科学学院", "计算机与信息科学学院 软件学院", "生命科学学院",
  "药学院", "动物科学技术学院", "动物医学院", "农学与生物科技学院", "植物保护学院",
  "园艺园林学院", "水产学院", "蚕桑纺织与生物质科学学院", "体育学院", "音乐学院",
  "美术学院", "新闻传媒学院", "教育学部", "心理学部", "国家治理学院"
];

Page({
  data: {
    form: {
      username: "",
      phone: "",
      student_id: "",
      grade: "",
      college: "",
      major: "",
      avatar: ""
    },
    gradeOptions,
    collegeOptions,
    gradeIndex: 0,
    collegeIndex: 0
  },

  onLoad() {
    this.loadProfile();
  },

  loadProfile() {
    wx.showLoading({ title: "加载中..." });
    me()
      .then((res) => {
        const u = res?.data || {};
        const gradeIndex = Math.max(0, gradeOptions.indexOf(u.grade || ""));
        const collegeIndex = Math.max(0, collegeOptions.indexOf(u.college || ""));
        this.setData({
          form: {
            username: u.username || "",
            phone: u.phone || "",
            student_id: u.student_id || "",
            grade: u.grade || gradeOptions[gradeIndex],
            college: u.college || collegeOptions[collegeIndex],
            major: u.major || "",
            avatar: u.avatar || ""
          },
          gradeIndex,
          collegeIndex
        });
      })
      .catch(() => wx.showToast({ title: "加载失败", icon: "none" }))
      .finally(() => wx.hideLoading());
  },

  onInput(e) {
    const key = e.currentTarget.dataset.key;
    this.setData({ [`form.${key}`]: e.detail.value || "" });
  },

  onGradeChange(e) {
    const idx = Number(e.detail.value);
    this.setData({
      gradeIndex: idx,
      "form.grade": gradeOptions[idx]
    });
  },

  onCollegeChange(e) {
    const idx = Number(e.detail.value);
    this.setData({
      collegeIndex: idx,
      "form.college": collegeOptions[idx]
    });
  },

  chooseAvatar() {
    wx.chooseImage({
      count: 1,
      sizeType: ["compressed"],
      sourceType: ["album", "camera"],
      success: (res) => {
        const path = res.tempFilePaths?.[0];
        if (path) this.setData({ "form.avatar": path });
      }
    });
  },

  submit() {
    const payload = { ...this.data.form };
    if (!payload.username) {
      wx.showToast({ title: "请输入昵称", icon: "none" });
      return;
    }
    wx.showLoading({ title: "保存中..." });
    updateProfile(payload)
      .then(() => {
        wx.showToast({ title: "保存成功", icon: "none" });
        setTimeout(() => wx.navigateBack(), 400);
      })
      .catch((err) => {
        wx.showToast({ title: err?.message?.slice(0, 20) || "保存失败", icon: "none" });
      })
      .finally(() => wx.hideLoading());
  }
});
