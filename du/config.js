/**
 * 小程序配置文件
 */

var host = 'https://465712482.ijason.club';

var config = {

    // 下面的地址配合云端 Demo 工作
    service: {
        host,
        
        // 语音识别接口
        voiceUrl: `${host}/recite/recognize`

        // recite上传接口
        reciteUploadUrl:`${host}/recite/upload`
    },

    //最大长度
    maxMinutes:10
};

module.exports = config;
