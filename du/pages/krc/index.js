// pages/krc/index.js
const poetryhelper= require('../../utils/poetryhelper.js')
const recitehelper= require('../../utils/recitehelper.js')


Page({

  /**
   * 页面的初始数据
   */
  data: {
    ssss:"sssssssssssssssssssssssssss",
      wcss:{}
  },

  /**
   * 生命周期函数--监听页面加载
   */
  onLoad: function (options) {
    //let classic = "春晓\n王维\n春眠不觉晓，\n处处闻啼鸟。\n夜来风雨声，\n花落知多少。";
    //let classic = "春|晓\n王,400|维\n春|眠|不|觉|晓|，\n处|处|闻|啼|鸟|。\n夜|来|风|雨|声|，\n花|落|知|多|少|。";
    let classic = "春|晓\n作|者|：|王|维\n春|眠|-|不|觉|晓|\n处|处|-|闻|啼|鸟\n夜|来|-|风|雨|声\n花|落|-|知|多|少";

    var self = this;

    this.poetry = new poetryhelper.PoetryHelper({
        durPerStep:30,
        stepPerLette:14,
        pageData:self.data,
        setData:function(data){self.setData(data)},
        cb_show:self.showPoetry,
        cb_finish:self.playFinish
    });
    
    this.ifFollow = true;
    this.poetry.parse(classic,self.ifFollow);

/*
    setTimeout(function(){
        self.setData({
            //author:{css:'author', da:[author]},
            ssss:11111111,
            //wcss:[["gres_30","gres_60"]]
        })
        re.play(self.playFinish);
    }, 5000);
*/
    console.log(self.data.ssss);
  },

  showPoetry:function(begin, lines){
        self.setData({
            begin:begin,
            wordLines:lines
        })
    },

  playFinish: function() {
      console.log('playFinished!!!!!!!!!!');
  },

  /**
   * 生命周期函数--监听页面初次渲染完成
   */
  onReady: function () {
  
  },

  /**
   * 生命周期函数--监听页面显示
   */
  onShow: function () {
  
  },

  /**
   * 生命周期函数--监听页面隐藏
   */
  onHide: function () {
  
  },

  /**
   * 生命周期函数--监听页面卸载
   */
  onUnload: function () {
  
  },

  /**
   * 页面相关事件处理函数--监听用户下拉动作
   */
  onPullDownRefresh: function () {
  
  },

  /**
   * 页面上拉触底事件的处理函数
   */
  onReachBottom: function () {
  
  },

  /**
   * 用户点击右上角分享
   */
  onShareAppMessage: function () {
  
  }
})


