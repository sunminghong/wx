const config = require('../config.js');

const formatTime = date => {
  const year = date.getFullYear()
  const month = date.getMonth() + 1
  const day = date.getDate()
  const hour = date.getHours()
  const minute = date.getMinutes()
  const second = date.getSeconds()

  return [year, month, day].map(formatNumber).join('/') + ' ' + [hour, minute, second].map(formatNumber).join(':')
}

const formatNumber = n => {
  n = n.toString()
  return n[1] ? n : '0' + n
}

//正则判断
const regular =function (str, reg) {
  if (reg.test(str))
    return true;
  return false;
}

//是否为中文
const isChinese= str => {
  var reg = /^[\u0391-\uFFE5]+$/;
  return Regular(str, reg);
}


//取得屏幕宽高，单位微rpx
const getScreenWH = ()=> { 
    try {
      var res = wx.getSystemInfoSync()
      console.log(res.model)
      console.log(res.pixelRatio)
      console.log('width:',res.windowWidth)
      console.log('height',res.windowHeight)
      console.log(res.language)
      console.log(res.version)
      console.log(res.platform)
      //return [res.pixelRatio * res.windowWidth, res.pixelRatio * res.windowHeight]
      return [2 * res.windowWidth, 2 * res.windowHeight - 128 * (res.pixelRatio - 2)]
    } catch (e) {
      //return [750, 1334]
    }
}


// 显示繁忙提示
var showBusy = text => wx.showToast({
    title: text,
    icon: 'loading',
    duration: 30000
})

// 显示成功提示
var showSuccess = text => wx.showToast({
    title: text,
    icon: 'success'
})

// 显示失败提示
var showModel = (title, content) => {
    wx.hideToast();

    wx.showModal({
        title,
        content: JSON.stringify(content),
        showCancel: false
    })
}

var showTips = tips => wx.showToast({
    title: tips,
    image: '/utils/warning.png',
    duration: 2000
})


var uploadFile=param => {
    if(config.enableNetwork) {
        param['url'] = config.service.reciteUploadUrl;
        wx.uploadFile(param)
    } else {
        console.log('uploadFile', formData);
    }
}

var uploadRecognizeVoice = param => {
    if(config.enableNetwork) {
        param['url'] = config.service.recognizeUrl;
        wx.uploadFile(param)
    } else {
        console.log('uploadFile', formData);
    }
}


var setStorage =param =>{
    wx.setStorage(param);
}

var getStorageSync = key =>{
 return wx.getStorageSync('recites');
}

function formatRecordTime(time) {
  if (typeof time !== 'number' || time < 0) {
    return time
  }

  var hour = parseInt(time / 3600)
  time = time % 3600
  var minute = parseInt(time / 60)
  time = time % 60
  var second = time

  return ([hour, minute, second]).map(function (n) {
    n = n.toString()
    return n[1] ? n : '0' + n
  }).join(':')
}

function formatLocation(longitude, latitude) {
  if (typeof longitude === 'string' && typeof latitude === 'string') {
    longitude = parseFloat(longitude)
    latitude = parseFloat(latitude)
  }

  longitude = longitude.toFixed(2)
  latitude = latitude.toFixed(2)

  return {
    longitude: longitude.toString().split('.'),
    latitude: latitude.toString().split('.')
  }
}


module.exports = { formatTime, formatRecordTime, formatLocation, isChinese, getScreenWH, showBusy, showSuccess, showModel, showTips }


