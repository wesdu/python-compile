#coding:utf-8

prefix = '/* Copyright (c) 2011, Tencent Qplus. All Rights Reserved. %s */\n' #会加入到压缩文件的头部 %s 会替换为SVN 'Last Changed Date'

rules = {
	"vm" : {
		"target" : './public/vm/js/vm.js',
		"source" : './tools/qzmin/vm.js.qzmin',
	},
	"ver" : {
		"target" : './public/vm/js/version.js',
		"source" : './tools/qzmin/version.js.qzmin',
	},
	"api": {
		"target" : './public/js/qplus.api.js',
		"source" : './tools/qzmin/qplus.api.js.qzmin',
	},
	"debugapi": {
		"target" : './public/js/qplus.api.js',
		"source" : './tools/qzmin/qplus.api.debugger.js.qzmin',
	},
	"statichtml": {
		"target" : './public/',
		"source" : './',
		"recursive" : False, #不填默认为False 开启为True, 开启则表示递归复制
		"ext": ["html", "htm"], #不填默认为任意后缀
	},
	"test": {
		"target" : './public/test/',
		"source" : './test/',
		"recursive" : True, #不填默认为False 开启为True
	},
	"test2": {
		"target" : './public/aaa/xxx.xxx.js',
		"source" : './assets/js/version.js',
	},
	"test3": {
		"target" : './public/test3/',
		"source" : './test/',
		"recursive" : True, #不填默认为False 开启为True
		"ext": ["html", "htm"], #不填默认为任意后缀
	},
	"test4": { #css combine
		"target" : './public/test4/main.css',
		"source" : './tools/qzmin/qqweb.main.css.qzmin',
	},
	"test5": {
		"target" : './public/',
		"source" : './testcss/',
	},
	"test6": {
		"target" : './public/aaa/',
		"source" : './assets/js/version.js',
	},
}

modes = {
	"-test" : ["debugapi", "vm", "ver", "statichtml", "test", "test2", "test3", "test4", "test5", "test6"],
	"-debug" : ["debugapi", "vm", "ver", "statichtml"],
	"-produce" : ["api", "vm", "ver", "statichtml"],
}

revisionMark = '%Revision%' #建议不要使用$Revision$ 这样的替换词，很容易与svn keywords混淆
googleclosurePath = './tools/compile/compiler.jar' 
yuicompiressorPath = './tools/compile/yuicompressor-2.4.7.jar'
revisionUpdatefiles = ["base.js", "version.js"] #这些文件中含有 %Revision% 的地方会被替换为SVN版本号