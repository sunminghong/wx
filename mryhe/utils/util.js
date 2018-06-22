/**
 * 请求网络
 */
function request( url, page, success, fail ) {
  if( typeof success != 'function' || typeof fail != 'function' ) {
    return
  }
  var app = getApp()
  wx.request( {
    url: url,
    data: {
      showapi_appid: app.globalData.showapi_appid,
      showapi_sign: app.globalData.showapi_sign,
      page: page,
      maxResult: app.globalData.maxResult,
      time: app.globalData.showapi_timestamp
    },
    success: function( res ) {
      if (res.statusCode == 200 ) {
        success( res.data )
      } else {
        fail(res.errMsg )
      }
    },
    fail: function() {
      fail( '网络错误' )
    }

  })
}

module.exports = {
  request: request
}
