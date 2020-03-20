# androidSrcReader

请在百度网盘下载数据与代码
链接：https://pan.baidu.com/s/1b8V_qSuuOHMj2R4INJne8w 
提取码：m15t

##  如何使用：

>1. 下载到本地解压后，将androidSrc.zip与data_.zip解压到当前文件夹，双击run.cmd（windows系统，软件要求 python3）就可以了，linux也可以运行，自行改后缀不多说<br/>
>2. run.cmd开始运行时会加载2g多的数据（data_.rar中的数据），并不会打印加载进度，如果你看到内存正在猛增或居高不下，那还得耐心等待<br/>
>3. 加载结束时会打印出你的局域网ip和端口号8888，这时你就可以打开浏览器，地址栏输入： http://localhost:8888/android.view.View.View::Context,AttributeSet,int,int: （包括最后的冒号），就进入了View类的构造函数，我们从这个函数开始，看看这个工具如何帮你读代码

## 这个工具如何帮你读安卓代码
### 1. 查看类
#### a. 类的父类和子类
![](https://github.com/doubledong94/android-source-reader/blob/master/pics/class_super_and_sub_types.PNG?raw=true)
#### b. 类中的属性和方法
![](https://github.com/doubledong94/android-source-reader/blob/master/pics/class_fields.PNG?raw=true)
![](https://github.com/doubledong94/android-source-reader/blob/master/pics/class_methods.PNG?raw=true)
#### c. 类内属性与方法的依赖关系
![](https://github.com/doubledong94/android-source-reader/blob/master/pics/field_dependency.PNG?raw=true)
![](https://github.com/doubledong94/android-source-reader/blob/master/pics/method_dependency.PNG?raw=true)
#### d. 类所产生的实例（包括局部变量）
![](https://github.com/doubledong94/android-source-reader/blob/master/pics/class_instance_for_field.PNG?raw=true)
![](https://github.com/doubledong94/android-source-reader/blob/master/pics/class_instance_for_local_variable.PNG?raw=true)
### 2. 查看函数
#### a. 函数的源码
![](https://github.com/doubledong94/android-source-reader/blob/master/pics/method_src.PNG?raw=true)
#### b. 函数的参数与返回
![](https://github.com/doubledong94/android-source-reader/blob/master/pics/method_parameter_and_return.PNG?raw=true)
#### c. 函数中语句的分类统计
![](https://github.com/doubledong94/android-source-reader/blob/master/pics/method_features.PNG?raw=true)
![](https://github.com/doubledong94/android-source-reader/blob/master/pics/method_feature14.PNG?raw=true)
![](https://github.com/doubledong94/android-source-reader/blob/master/pics/method_feature15.PNG?raw=true)
#### d. 函数中局部变量的使用情况
![](https://github.com/doubledong94/android-source-reader/blob/master/pics/method_all_local_variables.PNG?raw=true)
![](https://github.com/doubledong94/android-source-reader/blob/master/pics/method_local_variable_usage.PNG?raw=true)
![](https://github.com/doubledong94/android-source-reader/blob/master/pics/method_local_variable_src.PNG?raw=true)
#### e. 函数内局部变量的依赖情况
![](https://github.com/doubledong94/android-source-reader/blob/master/pics/local_variable_dependency.PNG?raw=true)
#### f. 函数所产生的属性的读写（局部变量的过渡作用已考虑在内）
![](https://github.com/doubledong94/android-source-reader/blob/master/pics/method_field_read_and_write.PNG?raw=true)
### 3. 查看属性
#### a. 属性的类型
#### b. 属性的源码
#### c. 属性被读写的统计情况
![](https://github.com/doubledong94/android-source-reader/blob/master/pics/field_src_and_features.PNG?raw=true)
![](https://github.com/doubledong94/android-source-reader/blob/master/pics/field_feature.PNG?raw=true)
#### d. 属性被读写的具体情况
![](https://github.com/doubledong94/android-source-reader/blob/master/pics/field_is_read_by.PNG?raw=true)
![](https://github.com/doubledong94/android-source-reader/blob/master/pics/field_is_written_by.PNG?raw=true)

