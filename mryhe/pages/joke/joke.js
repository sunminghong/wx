var http = require( '../../utils/util' )
var app = getApp()
var url = 'https://route.showapi.com/341-1'

Page( {
  data: {
    page: 1,
    loadingHide: false,
    hideFooter: true,
    jokeList: [],
  },
  onShareAppMessage: function (res) {
    if (res.from === 'button') {
      // 来自页面内转发按钮
      console.log(res.target)
    }
    return {
      title: '曾经有一段笑话我没有好好珍惜......',
      path: '/pages/joke/joke'
    }
  },
  onLoad: function( options ) {
    // 页面初始化 options为页面跳转所带来的参数
    var that = this
    //请求笑话列表
    http.request( url, this.data.page, function( dataJson ) {
      var content = '';
      for (var i = 0; i < dataJson.showapi_res_body.contentlist.length; i++) {
        const text = dataJson.showapi_res_body.contentlist[i].text.split('<p>').join('').split('</p>').join('').split('<br>').join('').split('<br />').join('');
        dataJson.showapi_res_body.contentlist[i].text = text;
      }  
      
      that.setData( {
        jokeList: that.data.jokeList.concat(dataJson.showapi_res_body.contentlist ),
        loadingHide: true
      })
    }, function( reason ) {
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
    //请求笑话列表
    http.request( url, ++this.data.page, function( dataJson ) {
      console.log(dataJson)

      var content = '';
      for (var i = 0; i < dataJson.showapi_res_body.contentlist.length; i++) {
          dataJson.showapi_res_body.contentlist[i].text = dataJson.showapi_res_body.contentlist[i].text.split('<p>').join('').split   ('</p>').join('').split('<br>').join('').split('<br />').join('');
      }

      that.setData( {
        jokeList: that.data.jokeList.concat(dataJson.showapi_res_body.contentlist ),
        hideFooter: !that.data.hideFooter
      })
    }, function( reason ) {
      console.log( reason )
      that.setData( {
        hideFooter: !that.data.hideFooter
      })
    })


  },

})