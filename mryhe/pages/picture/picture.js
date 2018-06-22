var app = getApp()
var http = require( '../../utils/util' )
var url = 'https://route.showapi.com/341-2'
Page( {
  data: {
    page: 1,
    loadingHide: false,
    hideFooter: true,
    picList: []
  },
  onShareAppMessage: function (res) {
    if (res.from === 'button') {
      // 来自页面内转发按钮
      console.log(res.target)
    }
    return {
      title: '曾经有一副趣图我没有好好珍惜......',
      path: '/pages/picture/picture'
    }
  },
  onLoad: function( options ) {
    // 页面初始化 options为页面跳转所带来的参数
    var that = this
    //请求笑话列表
    http.request( url, this.data.page, function( dataJson ) {

      console.log(dataJson.showapi_res_body.contentlist )

      that.setData( {
        picList: that.data.picList.concat(dataJson.showapi_res_body.contentlist ),
        loadingHide: true
      })
    }, function( reason ) {
      console.log( reason )
      that.setData( {
        loadingHide: true
      })
    })
  },

  /**
   * 滑动到底部加载更多
   */
  loadMore() {
    //请求笑话列表
    var that = this
    //显示footer
    this.setData( {
      hideFooter: !this.data.hideFooter
    })
    http.request( url, ++this.data.page, function( dataJson ) {
      that.setData( {
        picList: that.data.picList.concat(dataJson.showapi_res_body.contentlist ),
        hideFooter: !that.data.hideFooter
      })
    }, function( reason ) {
      console.log( reason )
      that.setData( {
        hideFooter: !that.data.hideFooter
      })
    })
  },

  preview( e ) {
    console.log( e.target.dataset.url )
    var urls = []
    urls.push( e.target.dataset.url )
    wx.previewImage( {
      urls: urls // 需要预览的图片http链接列表
    })
  }

})