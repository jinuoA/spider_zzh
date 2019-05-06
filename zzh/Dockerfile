FROM python2

# 维护者
MAINTAINER Pings 275598139@qq.com

# 环境变量
ENV LANG en_US.UTF-8
# 设置时区
RUN ln -s -f /usr/share/zoneinfo/Asia/Shanghai /etc/localtime

# 安装依赖
RUN yum install -y wget net-tools
--------------------- 
作者：Pingszi 
来源：CSDN 
原文：https://blog.csdn.net/zhouping118/article/details/81559646 
版权声明：本文为博主原创文章，转载请附上博文链接！

COPY zzh /root/docker/dev/

RUN pip install -r /root/docker/dev/requirements.txt -i https://pypi.douban.com/simple/

WORKDIR /root/docker/dev/zzh/
CMD ['python run.py']