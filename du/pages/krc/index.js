// pages/krc/index.js
const poetryhelper= require('../../utils/poetryhelper.js')
const recitehelper= require('../../utils/recitehelper.js')
const util= require('../../utils/util.js')
var playTimeInterval
var recordTimeInterval


Page({

  /**
   * 页面的初始数据
   */
  data: {
    ssss:"sssssssssssssssssssssssssss",
      wcss:{},
          recording: false,
    playing: false,
    hasRecord: false,
    recordTime: 0,
    playTime: 0,
    formatedRecordTime: '00:00:00',
    formatedPlayTime: '00:00:00',

      scene: "input",
    peotryInputHeight:0,

        s_poetry : "",
      samplePoetry:"",
  },


  /**
   * 生命周期函数--监听页面加载
   */
  onLoad: function (options) {

    let wh = util.getScreenWH();
    let ww = wh[0];
    let hh = wh[1];
      this.hh = hh;

     let s ="春|晓\n作|者|：|王|维\n春|眠|-|不|觉|晓\n处|处|-|闻|啼|鸟\n夜|来|-|风|雨|声\n花|落|-|知|多|少";

        this.setData({
            scene: "input",
            peotryInputHeight: hh - 150 - 30,
            poetryHeight:hh - 150 - 30,
            samplePoetry: s
        });
    this.enterInputScene();

  console.log(hh, this.data.peotryInputHeight);
  },

    switchScene: function() {
        this._enterScenes[this.scene]();
    },

    enterInputScene: function(){

    },

    textareaChange: function(e) {
        this.s_poetry = e.detail.value;

    },

  enterRecordFollowScene: function(e) {
      let self = this;
      setTimeout(function(){
          self._enterRecordFollow();
      },300);

  },

    _enterRecordFollow:function() {
    //let classic = "春晓\n王维\n春眠不觉晓，\n处处闻啼鸟。\n夜来风雨声，\n花落知多少。";
    //let classic = "春|晓\n王,400|维\n春|眠|不|觉|晓|，\n处|处|闻|啼|鸟|。\n夜|来|风|雨|声|，\n花|落|知|多|少|。";
    //let classic = "春|晓\n作|者|：|王|维\n春|眠|-|不|觉|晓|\n处|处|-|闻|啼|鸟\n夜|来|-|风|雨|声\n花|落|-|知|多|少";
    var self = this;
      

    this.poetry = new poetryhelper.PoetryHelper({
        durPerStep:30,
        stepPerLetter:14,
        pageData:self.data,
        fn_pageSetData:function(data){self.setData(data)},
        cb_show:self.showPoetry,
        cb_finish:self.playFinish
    });
    
    this.ifFollow = true;
    this.poetry.parse(this.s_poetry);

    this.setData({
            scene: "recordFollow",
        });

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
        this.setData({
            begin:begin,
            wordLines:lines
        })
    },

  startRecord: function(e) {
      this.poetry.play(this.ifFollow);
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
  
  },

  onHide: function() {
    if (this.data.playing) {
      this.stopVoice()
    } else if (this.data.recording) {
      this.stopRecordUnexpectedly()
    }
  },
  startRecord: function () {
    this.setData({ recording: true })

    var that = this
    recordTimeInterval = setInterval(function () {
      var recordTime = that.data.recordTime += 1
      that.setData({
        formatedRecordTime: util.formatRecordTime(that.data.recordTime),
        recordTime: recordTime
      })
    }, 1000)
    wx.startRecord({
      success: function (res) {
        that.setData({
          hasRecord: true,
          tempFilePath: res.tempFilePath,
          formatedPlayTime: util.formatRecordTime(that.data.playTime)
        })
      },
      complete: function () {
        that.setData({ recording: false })
        clearInterval(recordTimeInterval)
      }
    })
  },
  stopRecord: function() {
    wx.stopRecord()
  },
  stopRecordUnexpectedly: function () {
    var that = this
    wx.stopRecord({
      success: function() {
        console.log('stop record success')
        clearInterval(recordTimeInterval)
        that.setData({
          recording: false,
          hasRecord: false,
          recordTime: 0,
          formatedRecordTime: util.formatRecordTime(0)
        })
      }
    })
  },
  playVoice: function () {
    var that = this
    playTimeInterval = setInterval(function () {
      var playTime = that.data.playTime + 1
      console.log('update playTime', playTime)
      that.setData({
        playing: true,
        formatedPlayTime: util.formatRecordTime(playTime),
        playTime: playTime
      })
    }, 1000)
    wx.playVoice({
      filePath: this.data.tempFilePath,
      success: function () {
        clearInterval(playTimeInterval)
        var playTime = 0
        console.log('play voice finished')
        that.setData({
          playing: false,
          formatedPlayTime: util.formatRecordTime(playTime),
          playTime: playTime
        })
      }
    })
  },
  pauseVoice: function () {
    clearInterval(playTimeInterval)
    wx.pauseVoice()
    this.setData({
      playing: false
    })
  },
  stopVoice: function () {
    clearInterval(playTimeInterval)
    this.setData({
      playing: false,
      formatedPlayTime: util.formatRecordTime(0),
      playTime: 0
    })
    wx.stopVoice()
  },
  clear: function () {
    clearInterval(playTimeInterval)
    wx.stopVoice()
    this.setData({
      playing: false,
      hasRecord: false,
      tempFilePath: '',
      formatedRecordTime: util.formatRecordTime(0),
      recordTime: 0,
      playTime: 0
    })
  }
})
