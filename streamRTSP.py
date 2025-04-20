import os
import gi
import argparse
import signal
import sys
import socket

# Yeu cau phien ban GStreamer 1.0
gi.require_version('Gst', '1.0')
gi.require_version('GstRtspServer', '1.0')
from gi.repository import Gst, GstRtspServer, GLib

class MayChuRTSPCamera:
    def __init__(self, nguon_video='/dev/video0', 
                 rong=640, cao=480, 
                 khung_hinh=30, cong=8554, 
                 duong_dan="/camera", ma_hoa="h264",
                 ip_address=None):
        """
        Khoi tao may chu RTSP voi camera
        
        Tham so:
            nguon_video: Nguon video (mac dinh: /dev/video0)
            rong: Chieu rong video (mac dinh: 640)
            cao: Chieu cao video (mac dinh: 480)
            khung_hinh: Toc do khung hinh (mac dinh: 30)
            cong: Cong RTSP (mac dinh: 8554)
            duong_dan: Duong dan RTSP (mac dinh: /camera)
            ma_hoa: Ma hoa video (mac dinh: h264, co the la: h264, mjpeg)
            ip_address: Dia chi IP may chu (mac dinh: lay IP tu he thong)
        """
        self.nguon_video = nguon_video
        self.rong = rong
        self.cao = cao
        self.khung_hinh = khung_hinh
        self.cong = cong
        self.duong_dan = duong_dan
        self.ma_hoa = ma_hoa
        
        # Lay dia chi IP
        if ip_address:
            self.ip_address = ip_address
        else:
            # Lay dia chi IP mac dinh
            try:
                s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                s.connect(("8.8.8.8", 80))
                self.ip_address = s.getsockname()[0]
                s.close()
            except:
                self.ip_address = "127.0.0.1"
        
        # Khoi tao GStreamer
        Gst.init(None)
        
        # Tao main loop
        self.vong_chinh = GLib.MainLoop()
        
        # Tao may chu RTSP
        self.may_chu = GstRtspServer.RTSPServer()
        self.may_chu.set_service(str(self.cong))
        
        # Tao factory cho media
        self.nha_may = GstRtspServer.RTSPMediaFactory()
        self.nha_may.set_launch(self._tao_pipeline())
        self.nha_may.set_shared(True)
        
        # Gan factory vao duong dan cua may chu
        self.diem_mount = self.may_chu.get_mount_points()
        self.diem_mount.add_factory(self.duong_dan, self.nha_may)
        
        # Gan tin hieu de xu ly ket noi client
        self.may_chu.connect("client-connected", self._client_ket_noi)
        
    def _tao_pipeline(self):
        """Tao pipeline GStreamer cho viec stream video tu camera"""
        phan_pipeline = [
            f"v4l2src device={self.nguon_video}",
            f"video/x-raw,width={self.rong},height={self.cao},framerate={self.khung_hinh}/1",
            "videoconvert"
        ]
        
        if self.ma_hoa == "h264":
            phan_pipeline.extend([
                "x264enc tune=zerolatency speed-preset=ultrafast bitrate=1000",
                "h264parse",
                "rtph264pay name=pay0 pt=96"
            ])
        elif self.ma_hoa == "mjpeg":
            phan_pipeline.extend([
                "jpegenc quality=85",
                "rtpjpegpay name=pay0"
            ])
        else:
            raise ValueError(f"Ma hoa khong duoc ho tro: {self.ma_hoa}")
        
        return " ! ".join(phan_pipeline)
    
    def _client_ket_noi(self, may_chu, client):
        """Ham callback khi client ket noi den may chu RTSP"""
        print(f"Client ket noi: {client.get_connection().get_ip()}")
    
    def chay(self):
        """Khoi dong may chu RTSP"""
        self.may_chu.attach(None)
        print(f"May chu RTSP dang chay tai: rtsp://{self.ip_address}:{self.cong}{self.duong_dan}")
        signal.signal(signal.SIGINT, self._xu_ly_thoat)
        
        try:
            self.vong_chinh.run()
        except KeyboardInterrupt:
            pass
    
    def _xu_ly_thoat(self, tin_hieu, khung):
        """Xu ly tin hieu thoat ung dung"""
        print("Tat may chu RTSP...")
        self.vong_chinh.quit()

def main():
    """Ham main de xu ly tham so dong lenh va khoi dong may chu"""
    parser = argparse.ArgumentParser(description='May chu RTSP Camera cho Raspberry Pi')
    
    parser.add_argument('--source', type=str, default='/dev/video0',
                        help='Nguon video (mac dinh: /dev/video0)')
    parser.add_argument('--width', type=int, default=640,
                        help='Chieu rong video (mac dinh: 640)')
    parser.add_argument('--height', type=int, default=480,
                        help='Chieu cao video (mac dinh: 480)')
    parser.add_argument('--fps', type=int, default=30,
                        help='Toc do khung hinh (mac dinh: 30)')
    parser.add_argument('--port', type=int, default=8554,
                        help='Cong RTSP (mac dinh: 8554)')
    parser.add_argument('--path', type=str, default='/camera',
                        help='Duong dan RTSP (mac dinh: /camera)')
    parser.add_argument('--encoding', type=str, default='h264', choices=['h264', 'mjpeg'],
                        help='Ma hoa video: h264 hoac mjpeg (mac dinh: h264)')
    parser.add_argument('--ip', type=str, default=None,
                        help='Dia chi IP may chu (mac dinh: tu dong phat hien)')
    
    args = parser.parse_args()
    
    if not os.path.exists(args.source):
        print(f"Loi: Khong tim thay nguon video '{args.source}'")
        return 1
    
    may_chu = MayChuRTSPCamera(
        nguon_video=args.source,
        rong=args.width,
        cao=args.height,
        khung_hinh=args.fps,
        cong=args.port,
        duong_dan=args.path,
        ma_hoa=args.encoding,
        ip_address=args.ip
    )
    
    may_chu.chay()
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
