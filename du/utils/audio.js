const config = require('../config');
const util = require('util');
const dateformat = require('dateformat');

let recorderManager = null;
let innerAudioContext = null;


// 是否有文件正在播放
let isPlayingVoice = false;
// 正在播放的文件名
let playingVoiceKey = '';
// 正在播放的文件索引
let playingVoiceIndex = 0;

/**
 * PAGE 相关代码
 */
class AudioHelper {
    recites: [],

    constructor(pageData, pageSetDataFn) {
      this.pageData = pageData;
      this.setDataFn = pageSetDatafn;

        // 读取储存着的笔记
        let recites = JSON.parse(wx.getStorageSync('recites') || '[]');

        // 添加播放标记
        recites = recites.map(v => {
            v.playing = false;
            
            if (v.isRec === true && !v.word) {
                v.isRec = false;
            }

            return v;
        })

        this.recites = recites;
    },

    _getData (key) {
      return this.pageData ? this.pageData[key]:null;
    },

    _setData (key) {
      this.setDataFn && this.setDataFn(data);
    },

    getVoices() {
        return this.recites;
    },

    initAudio() {
        innerAudioContext = wx.createInnerAudioContext();
    },

    //播放声音，参数为对象
    playVoice(param) {
        let e = param;
        const path = e.path;
        const key = e.key;
        const idx = e.idx;

        const recites = this.recites;

        /**
         * 如果有文件正在播放
         * 则停止正在播放的文件
         */
        if (isPlayingVoice) {
            innerAudioContext.stop();
            isPlayingVoice = false;
            recites[playingVoiceIndex].playing = false;

            this._setData({ recites });
        }

        /**
         * 如果正在播放的文件就是点击的这个文件
         * 则视为停止不再播放
         */
        if (playingVoiceKey === key) {
            playingVoiceKey = '';
            return;
        }

        isPlayingVoice = true;
        playingVoiceKey = key;
        playingVoiceIndex = idx;

        recites[idx].playing = true;
        this.setData({ recites });

        console.log('play voice', key);
        innerAudioContext.src = path;
        innerAudioContext.play();

        // 播放时间到了置回未播放
        setTimeout(() => {
            recites[idx].playing = false;
            this.setData({ recites });
        }, recites[idx].duration * 1000);
    },

    //停止播放声音，参数为对象
    stopVoice(key) {
        const recites = this.data.recites.filter(v => v.key !== key);

        /**
         * 如果有文件正在播放
         * 则停止正在播放的文件
         */
        if (isPlayingVoice) {
            innerAudioContext.stop();
            isPlayingVoice = false;
            recites[0].playing = false;

            this._setData({ recites });
        }
    },

        /**
         * 如果正在播放的文件就是点击的这个文件
         * 则视为停止不再播放
         */

        /*
    showVoiceActions (voicekey) {
        const voice = this.recites.filter(v => v.key === voiceKey)[0];

        wx.showActionSheet({
            itemList: ['重新识别', '删除语音'],
            success: res => {
                if (res.tapIndex === 0) {
                    if (!voice.isRec || !voice.word) {
                        this.recognizeVoice(voice.key, voice.path);
                    }
                } else if (res.tapIndex === 1) {
                    this.deleteVoice(voiceKey);
                }
            }
        });
    },
        */

    deleteVoice (key) {
        const recites = this.data.recites.filter(v => v.key !== key);
        this.saveToStorage(recites);
        this.setData({ recites });
    },


    _initRecord() {
        // 处理录音逻辑
        recorderManager = wx.getRecorderManager();

        recorderManager.onStop(this.onVoiceStop);

        // this.recorderManager.onFrameRecorded(res => {
        //     const { frameBuffer, isLastFrame } = res
        //     console.log('frameBuffer.byteLength', frameBuffer.byteLength)
        //     this.recognizeVoice({
        //         data: wx.arrayBufferToBase64(frameBuffer),
        //         isLastFrame: isLastFrame
        //     })
        // });
    },

        //recite   {title:"春望",krc:"xxx|xxx|", text:""}
    startVoiceRecord (recite) {
        if (recorderManager)
            this._initRecord();

        this.currRecite = recite;

        console.log('start record');
        secorderManager.start({
            // 最大长度设置为 2 分钟
            duration: config.maxMinutes * 60 * 1000,
            // 格式
            format: 'mp3',
            sampleRate: 16000,
            encodeBitRate: 25600,
            frameSize: 9,
            numberOfChannels: 1
        });
    },

    stopVoiceRecord() {
        console.log('stop record');
        recorderManager.stop();
    },

    onVoiceStop (voiceInfo) {
        const { duration, tempFilePath } = voiceInfo;

        // 不允许小于 1 秒
        if (duration < 1000) {
            util.showTips('录音过短');
            return;
        }

        // 保存文件
        wx.saveFile({
            tempFilePath,
            success: fileInfo => {
                const { savedFilePath } = fileInfo;
                //const voiceKey = `voicerecite-${Date.now()}`

                // 生成笔记并保存再 storage
                let rec =  {
                    key: voiceKey,
                    path: savedFilePath,
                    duration: (duration / 1000).toFixed(2),
                    word: '',
                    isRec: false,
                    time: dateformat(new Date, 'YYYY-MM-DD HH:mm:ss')
                };

                this.currRecite.forEach(({k,v})=> rec[k] = v); 
                const recites = this.recites.map(v => v);
                recites.unshift(rec);//加到开头

                this.saveToStorage(recites);
                this._setData({ recites });
            },
            fail () {
                util.showModel('错误', '保存语音失败');
            }
        });
    },

    /**
     * 调用音频识别接口
     * @params {string} key 音频名称
     * @params {string} key 本地地址
     */
    recognizeVoice (key, path) {
        wx.uploadFile({
            url: config.service.voiceUrl,
            filePath: path,
            name: 'file',
            success: res => {
                let data = res.data;
                if (typeof data === 'string') {
                    data = JSON.parse(data);
                }

                console.log(res);

                if (data.code !== 0) {
                    console.error(data);
                    util.showModel('语音识别失败', data);
                    return;
                }

                const result = data.data.reduce((pre, cur, idx) => {
                    if (pre.hasError) {
                        return pre;
                    }

                    if (cur.code !== 0) {
                        pre.hasError = true;
                        pre.errMsg = message;
                    }

                    pre.text = cur.text;
                    return pre;
                }, { text: '', hasError: false, errMsg: '' });

                if (!result.hasError) {
                    const recites = this.data.recites.map(v => {
                        if (v.key === key) {
                            v.word = result.text;
                            v.isRec = true;
                        }
                        return v;
                    });

                    this.saveToStorage(recites);
                    this.setData({ recites });
                } else {
                    console.error(result, data);
                    util.showModel('语音识别失败', result.errMsg);
                }
            },
            fail: function (e) {
                console.error(e);
                util.showModel('语音识别失败', e);
            }
        });
    },

    saveToStorage (recites) {
        recites = recites.map(v => {
            delete v.playing;
            return v
        });

        wx.setStorage({
            key: 'recites',
            data: JSON.stringify(recites)
        })
    },

    uploadRecite (key) {
        const recite = this.data.recites.filter(v => v.key !== key);
        if (recite.length ==0)
            return;

        wx.uploadFile({
            url: config.service.reciteUploadUrl,
            filePath: recite.path,
            name: 'file',
            formData: recite,
            success: res => {
                let data = res.data;
                if (typeof data === 'string') {
                    data = JSON.parse(data);
                }

                console.log(res);

                if (data.code !== 0) {
                    console.error(data);
                    util.showModel('语音识别失败', data);
                    return;
                }

                const result = data.data.reduce((pre, cur, idx) => {
                    if (pre.hasError) {
                        return pre;
                    }

                    if (cur.code !== 0) {
                        pre.hasError = true;
                        pre.errMsg = message;
                    }

                    pre.text = cur.text;
                    return pre;
                }, { text: '', hasError: false, errMsg: '' });

                if (!result.hasError) {
                    const recites = this.data.recites.map(v => {
                        if (v.key === key) {
                            v.word = result.text;
                            v.isRec = true;
                        }
                        return v;
                    });

                    this.saveToStorage(recites);
                    this.setData({ recites });
                } else {
                    console.error(result, data);
                    util.showModel('语音识别失败', result.errMsg);
                }
            },
            fail: function (e) {
                console.error(e);
                util.showModel('语音识别失败', e);
            }
        });

    }


})
