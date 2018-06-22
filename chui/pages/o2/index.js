/**
 * 作者：happycxz
 * 最后更新时间：2017.11.09
 * 源码分享链接：http://www.happycxz.com/m/?p=125
 *
 * https的silk语音识别API（专供微信小程序调用）：https://api.happycxz.com/wxapp/silk2asr
 * https的mp3语音识别API（专供微信小程序调用）：https://api.happycxz.com/wxapp/mp32asr
 * 该API服务搭建全过程解析及源码分享贴：http://blog.csdn.net/happycxz/article/details/78016299
 * 需要使用此API请联系作者QQ：404499164
 * 
 * 遵循开放、分享、自由、免费的精神，把开源坚持到底
 */

//获取应用实例 
var app = getApp()
const global = app.globalData;
console.log(global.abc);
var AV = require('../../utils/mp3/aurora');
global.win_dow = { 'AV': AV };
console.log(AV.Player, AV.Base, global.win_dow.AV);
require('../../utils/mp3/mp3');

var UTIL = require('../../utils/util.js');
var GUID = require('../../utils/GUID.js');
//var NLI = require('../../utils/NLI.js');

//const appkey = require('../../config').appkey
//const appsecret = require('../../config').appsecret

try {
  const audioContext = new AudioContext();
} catch (e) {
  console.log('!妳的浏览器不支持AudioContext:(');
  console.log(e);
}

//微信小程序新录音接口，录出来的是aac或者mp3，这里要录成mp3
const mp3Recorder = wx.getRecorderManager()
const mp3RecoderOptions = {
  duration: 600000,
  sampleRate: 16000,
  numberOfChannels: 1,
  encodeBitRate: 48000,
  format: 'mp3',
  frameSize: 4
}

//弹幕定时器
var timer;

var pageSelf = undefined;

var doommList = [];
class Doomm {
  constructor() {
    //this.text = UTIL.getRandomItem(app.globalData.corpus);
    this.top = Math.ceil(Math.random() * 40);
    this.time = Math.ceil(Math.random() * 8 + 6);
    this.color = getRandomColor();
    this.display = true;
    let that = this;
    setTimeout(function () {
      doommList.splice(doommList.indexOf(that), 1);
      doommList.push(new Doomm());

      pageSelf.setData({
        doommData: doommList
      })
    }, this.time * 1000)
  }
}
function getRandomColor() {
  let rgb = []
  for (let i = 0; i < 3; ++i) {
    let color = Math.floor(Math.random() * 256).toString(16)
    color = color.length == 1 ? '0' + color : color
    rgb.push(color)
  }
  return '#' + rgb.join('')
}

Page({
  isDecoding: false,
  recSize: 0,
  data: {
    j: 1,//帧动画初始图片 
    isSpeaking: false,//是否正在说话
    outputTxt: "", //输出识别结果

    doommData: [],

  },

  initDoomm: function () {
    doommList.push(new Doomm());
    doommList.push(new Doomm());
    doommList.push(new Doomm());
    this.setData({
      doommData: doommList
    })
  },

  //frameBuffer :float32Array
  computeVolume: function (view) {
    const r = view.length;

    //const view=new Int8Array(frameBuffer);
    let pw = 0, v = 0;
    //将缓冲区内容按字节求平方和
    for (let i = 0; i < r; i++) {
      const c = view[i];

      v += c * c;

      let s = Math.max(-1, Math.min(1, c * 8));//PCM 音量直接放大8倍，失真还能接受
      s = s < 0 ? s * 0x8000 : s * 0x7FFF;
      pw += Math.abs(s);
    }
    const mean = v / r;
    const volume = 10 * Math.log10(mean);
    UTIL.log('bytes:', r, "v:", v, "mean:", mean, "volume:", volume);

    //求平均值，得到音量大小
    const power = pw / r;
    //计算分贝值
    let powerLevel = 0;
    if (power > 0) {
      //https://blog.csdn.net/jody1989/article/details/73480259
      powerLevel = Math.round(Math.max(0, (20 * Math.log10(power / 0x7fff) + 34) * 100 / 34));
    };

    //const volume = 10*Math.log10(mean);
    UTIL.log('bytes:', r, "power:", power, "volume:", powerLevel);

  },

  onLoad: function () {
    pageSelf = this;
    this.initDoomm();

    //onLoad中为录音接口注册两个回调函数，主要是onStop，拿到录音mp3文件的文件名（不用在意文件后辍是.dat还是.mp3，后辍不决定音频格式）
    mp3Recorder.onStart(() => {
      this.recSize = 0;
      UTIL.log('mp3Recorder.onStart()...')
    })

    mp3Recorder.onFrameRecorded((res) => {
      //if (this.isDecoding) return;
      this.isDecoding = true;
      const { frameBuffer, isLastFrame } = res
      let r = frameBuffer.byteLength;
      this.recSize += r;
      UTIL.log('frameBuffer.byteLength', r, this.recSize);

      let asset = AV.Asset.fromBuffer(frameBuffer);
      //let asset = AV.Asset.fromURL('http://mysite.com/test.wav');
      //var list = new AV.BufferList;
      let vv = 0;

      asset.on('error', function (e) {
        UTIL.log('mp3 asset err:', e);
      });
      // asset.on('data', function(buffer) {
      //   //list.push(new AV.Buffer(buffer));
      //   vv +=buffer.byteLength;
      // });
      //asset.start();

      // UTIL.log("vv:", vv);
      const that = this;

      try {
        asset.decodeToBuffer(function (buffer) {
          // buffer is now a Float32Array containing the entire decoded audio file
          UTIL.log("000vv:", vv);
          vv += buffer.byteLength;
          that.computeVolume(buffer); //调用_visualize进行下一步处理，此方法在后面定义并实现
          that.isDecoding = false;
        });
      } catch (e) {
        that.isDecoding = false;
        UTIL.log(e);
      }
      UTIL.log("vv:", vv);


    })

    mp3Recorder.onStop((res) => {
      UTIL.log('mp3Recorder.onStop() ' + res)
      const { tempFilePath, duration, fileSize } = res
      var urls = "https://api.happycxz.com/wxapp/mp32asr";
      UTIL.log('mp3Recorder.onStop() tempFilePath:' + tempFilePath, 'fileSize:', fileSize);




      //processFileUploadForAsr(urls, tempFilePath, this);
    })
  },

  /////////////////////////////////////////////////////////////// 以下是调用新接口实现的录音，录出来的是 mp3
  touchdown: function () {
    //touchdown_mp3: function () {
    UTIL.log("mp3Recorder.start with" + mp3RecoderOptions)
    var _this = this;
    speaking.call(this);
    this.setData({
      isSpeaking: true
    })
    mp3Recorder.start(mp3RecoderOptions);
  },
  touchup: function () {
    //touchup_mp3: function () {
    UTIL.log("mp3Recorder.stop")
    this.setData({
      isSpeaking: false,
    })
    mp3Recorder.stop();
  },


  //切换到老版本
  turnToOld: function () {
    wx.navigateTo({
      url: '../index/index',
    })
  },

  /////////////////////////////////////////////////////////////// 以下是调用老接口实现的录音，录出来的是 silk_v3
  //手指按下 
  touchdown_silk: function () {
    //touchdown: function () {
    UTIL.log("手指按下了... new date : " + new Date)
    var _this = this;
    speaking.call(this);
    this.setData({
      isSpeaking: true
    })
    //开始录音 
    wx.startRecord({
      success: function (res) {
        //临时路径,下次进入小程序时无法正常使用
        var tempFilePath = res.tempFilePath;
        UTIL.log('record SUCCESS file path:' + tempFilePath)
        _this.setData({
          recordPath: tempFilePath
        });
      },
      fail: function (res) {
        //录音失败 
        wx.showModal({
          title: '提示',
          content: '录音的姿势不对!',
          showCancel: false,
          success: function (res) {
            if (res.confirm) {
              UTIL.log('用户点击确定')
              return
            }
          }
        })
      }
    })
  },
  //手指抬起 
  touchup_silk: function () {
    //touchup: function () {
    UTIL.log("手指抬起了...")
    this.setData({
      isSpeaking: false,
    })
    clearInterval(this.timer)
    wx.stopRecord()

    var _this = this
    setTimeout(function () {
      var urls = "https://api.happycxz.com/wxapp/silk2asr/";
      UTIL.log(_this.data.recordPath);
      processFileUploadForAsr(urls, _this.data.recordPath, _this);
    }, 1000)
  },


})

/*
//上传录音文件到 api.happycxz.com 接口，处理语音识别和语义，结果输出到界面
function processFileUploadForAsr(urls, filePath, _this) {
  wx.uploadFile({
    url: urls,
    filePath: filePath,
    name: 'file',
    formData: { "appKey": appkey, "appSecret": appsecret, "userId": UTIL.getUserUnique() },
    header: { 'content-type': 'multipart/form-data' },
    success: function (res) {
      UTIL.log('res.data:' + res.data);

      var nliResult = getNliFromResult(res.data);
      UTIL.log('nliResult:' + nliResult);
      var stt = getSttFromResult(res.data);
      UTIL.log('stt:' + stt);

      //var sentenceResult;
      try {
        //sentenceResult = NLI.getSentenceFromNliResult(nliResult);
      } catch (e) {
        UTIL.log('touchup() 错误' + e.message + '发生在' + e.lineNumber + '行');
        //sentenceResult = '没明白你说的，换个话题？'
      }

      //var lastOutput = "==>语音识别结果：\n" + stt + "\n\n==>语义处理结果：\n" + sentenceResult;
      _this.setData({
        outputTxt: lastOutput,
      });
      wx.hideToast();
    },
    fail: function (res) {
      UTIL.log(res);
      wx.showModal({
        title: '提示',
        content: "网络请求失败，请确保网络是否正常",
        showCancel: false,
        success: function (res) {
        }
      });
      wx.hideToast();
    }
  });
}*/

function getNliFromResult(res_data) {
  var res_data_json = JSON.parse(res_data);
  var res_data_result_json = JSON.parse(res_data_json.result);
  return res_data_result_json.nli;
}

function getSttFromResult(res_data) {
  var res_data_json = JSON.parse(res_data);
  var res_data_result_json = JSON.parse(res_data_json.result);
  return res_data_result_json.asr.result;
}

//麦克风帧动画 
function speaking() {
  var _this = this;
  //话筒帧动画 
  var i = 1;
  this.timer = setInterval(function () {
    i++;
    i = i % 5;
    _this.setData({
      j: i
    })
  }, 200);
}