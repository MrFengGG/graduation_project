#!/bin/bash
echo "关闭家庭智能控制系统..."

echo "检测服务器模块运行状态..."
serverId=`ps -ef |grep 'server.js'|grep -v 'grep'|awk '{print $2}'`
echo $serverId
if [ ! $serverId ]; then
	echo "web服务器未运行"
else
	echo "web服务器已运行,PID:$serverId,关闭..."
	`kill -9 $serverId`
fi
echo "web服务器关闭完成"

echo "检测舵机控制模块运行状态..."
serverId=`ps -ef |grep 'control.py'|grep -v 'grep'|awk '{print $2}'`
if [ ! $serverId ]; then
	echo "舵机控制模块未运行"
else
	echo "舵机控制模块已运行,PID:$serverId,关闭..."
	`kill -9 $serverId`
fi
echo "舵机控制模块关闭完成"

echo "检测图像采集模块运行状态..."
serverId=`ps -ef |grep 'main.py'|grep -v 'grep'|awk '{print $2}'`
echo $serverId
if [ ! $serverId ]; then
	echo "图像采集模块未运行."
else
	echo "图像采集模块已运行,PID:$serverId,关闭..."
	`kill -9 $serverId`
fi
echo "图像采集模块关闭完成"

echo "检测网络穿透模块运行状态..."
serverId=`ps -ef |grep 'frpc'|grep -v 'grep'|awk '{print $2}'`
if [ ! $serverId ]; then
	echo "网络穿透模块未运行,关闭中..."
else
	echo "网络穿透模块已运行,PID:$serverId,"
	cd nat/
	./frpc -f frpc.ini &
	cd ../
fi
echo "网络穿透模块关闭完成"

echo "家庭智能控制系统关闭完毕"
