=========Các bước cài đặt packages quan trọng để streaming camera trên Raspberry Pi📷=========

Bước 1: Cập nhật hệ thống
sudo apt-get update
sudo apt-get upgrade

Bước 2: Cài đặt GStreamer core và các plugin cơ bản
sudo apt-get install \
  libgstreamer1.0-dev libgstreamer-plugins-base1.0-dev libgstreamer-plugins-bad1.0-dev \
  gstreamer1.0-plugins-base gstreamer1.0-plugins-good gstreamer1.0-plugins-bad \
  gstreamer1.0-plugins-ugly gstreamer1.0-libav gstreamer1.0-tools \
  gstreamer1.0-x gstreamer1.0-alsa gstreamer1.0-pulseaudio

Bước 3: Cài đặt gst‑rtsp‑server để tạo RTSP service
sudo apt-get install libgstrtspserver-1.0-dev


Bước 4: Cài đặt Python GObject Introspection để chạy server bằng Python
sudo apt-get install python3-gi gir1.2-gstreamer-1.0 gir1.2-gst-plugins-base-1.0 libgirepository1.0-dev

Bước 5: (Tùy chọn) Cài đặt bindings GStreamer cho Python
sudo apt-get install python3-gst-1.0
===Gói này chứa overrides cho GObject Introspection giúp Python thao tác trực tiếp với các lớp GStreamer=====

Trước khi chạy script bằng python3 yourCode.py, hãy chắc chắn bạn đã thoát hẳn môi trường ảo (bằng lệnh deactivate hoặc conda deactivate) để Python sử dụng đúng interpreter và thư viện hệ thống. 
Chạy file code thông qua cú pháp : python3 ___yourCode__.py
