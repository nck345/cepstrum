import os
import sys
sys.stdout.reconfigure(encoding='utf-8')
import glob
import numpy as np
import scipy.io.wavfile as wav
import scipy.signal as signal
import matplotlib.pyplot as plt
from cepstrum_utils import read_lab,extract_cepstrum_features,compute_frame_cepstrum
BASE_DIR=os.path.dirname(os.path.abspath(__file__))
TEST_DIR=os.path.join(BASE_DIR,'TinHieuKiemThu')
TRAIN_DIR=os.path.join(BASE_DIR,'TinHieuHuanLuyen_latest')
FIG_DIR=os.path.join(BASE_DIR,'figures')
os.makedirs(FIG_DIR,exist_ok=True)
plt.rcParams['font.sans-serif']='Arial'
plt.rcParams['axes.edgecolor']='#333333'
plt.rcParams['axes.linewidth']=0.8
plt.rcParams['grid.alpha']=0.4
plt.rcParams['grid.linestyle']='--'
def generate_test_contours(threshold=3.90):
	wav_files=sorted(glob.glob(os.path.join(TEST_DIR,'*.wav')))
	for wav_file in wav_files:
		bname=os.path.basename(wav_file)
		prefix=os.path.splitext(bname)[0]
		lab_file=os.path.splitext(wav_file)[0]+'.lab'
		gt_mean,gt_std,gt_num,_=read_lab(lab_file)
		fs,data=wav.read(wav_file)
		if data.ndim>1:
			data=data[:,0]
		data=data.astype(np.float32)
		dur=len(data)/fs
		time_signal=np.linspace(0,dur,len(data))
		time_axis,proms,k_stars,c_maxs,energies,k_min,k_max=extract_cepstrum_features(data,fs)
		f0_raw=np.where(proms>=threshold,fs/k_stars,0.0)
		f0_med=signal.medfilt(f0_raw,kernel_size=5)
		v=f0_med[f0_med>0]
		p_mean=float(np.mean(v)) if len(v)>0 else 0.0
		p_std=float(np.std(v)) if len(v)>0 else 0.0
		fig,(ax1,ax2)=plt.subplots(2,1,figsize=(12,7),dpi=150,sharex=True)
		ax1.plot(time_signal,data/np.max(np.abs(data)),color='#2B5B84',linewidth=0.8)
		ax1.set_title(f"DANG SONG AM THANH (WAVEFORM) - {bname}",fontsize=12,fontweight='bold')
		ax1.set_ylabel("Bien do chuan hoa",fontsize=10)
		ax1.grid(True)
		f0_plot=np.where(f0_med>0,f0_med,np.nan)
		ax2.scatter(time_axis,f0_plot,color='#D9381E',s=14,label=f'F0 Cepstrum (Pred Mean={p_mean:.1f}Hz, Std={p_std:.1f}Hz)')
		if gt_mean:
			ax2.axhline(gt_mean,color='#2CA02C',linestyle='--',linewidth=1.8,label=f'GT Mean={gt_mean:.1f}Hz, Std={gt_std:.1f}Hz (.lab)')
		ax2.set_title(f"DUONG BAO F0 CONTOUR DONG BO THEO THOI GIAN - {prefix}",fontsize=12,fontweight='bold')
		ax2.set_xlabel("Thoi gian (giay)",fontsize=10)
		ax2.set_ylabel("Tan so F0 (Hz)",fontsize=10)
		ax2.set_ylim(50,450)
		ax2.grid(True)
		ax2.legend(loc='upper right',fontsize=10)
		plt.tight_layout()
		out_path=os.path.join(FIG_DIR,f"{prefix}_f0_contour.png")
		plt.savefig(out_path)
		plt.close()
		print(f"Generated: {out_path}")
def generate_voiced_vs_unvoiced():
	wav_file=os.path.join(TRAIN_DIR,'phone_F1.wav')
	if not os.path.exists(wav_file):
		return
	fs,data=wav.read(wav_file)
	if data.ndim>1:
		data=data[:,0]
	data=data.astype(np.float32)
	fl=int(round(0.03*fs))
	k_min=int(round(fs/400.0))
	k_max=int(round(fs/70.0))
	n_fft=2048
	idx_v=int(round(0.8*fs))
	frame_v=data[idx_v:idx_v+fl]
	best_k_v,c_max_v,prom_v,cep_v=compute_frame_cepstrum(frame_v,fs,k_min,k_max,n_fft)
	idx_uv=int(round(0.2*fs))
	frame_uv=data[idx_uv:idx_uv+fl]
	best_k_uv,c_max_uv,prom_uv,cep_uv=compute_frame_cepstrum(frame_uv,fs,k_min,k_max,n_fft)
	quef_ms=np.arange(len(cep_v))*(1000.0/fs)
	fig,axs=plt.subplots(2,2,figsize=(13,8),dpi=150)
	t_v=np.arange(fl)*(1000.0/fs)
	axs[0,0].plot(t_v,frame_v/np.max(np.abs(frame_v)),color='#1F77B4')
	axs[0,0].set_title("KHUNG HUU THANH (VOICED) - SONG TUAN HOAN",fontsize=11,fontweight='bold')
	axs[0,0].set_xlabel("Thoi gian (ms)",fontsize=9)
	axs[0,0].set_ylabel("Bien do",fontsize=9)
	axs[0,0].grid(True)
	q_idx=np.arange(k_min,k_max+1)
	axs[0,1].plot(quef_ms[q_idx],cep_v[q_idx],color='#1F77B4',linewidth=1.5,label='Cepstrum')
	axs[0,1].scatter([best_k_v*1000.0/fs],[c_max_v],color='#D62728',s=60,zorder=5,label=f'Dinh T0={best_k_v*1000.0/fs:.2f}ms (F0={fs/best_k_v:.1f}Hz)')
	axs[0,1].set_title(f"CEPSTRUM KHUNG HUU THANH (Prominence={prom_v:.2f} >= 3.90)",fontsize=11,fontweight='bold')
	axs[0,1].set_xlabel("Quefrency (ms)",fontsize=9)
	axs[0,1].set_ylabel("Bien do Cepstrum",fontsize=9)
	axs[0,1].grid(True)
	axs[0,1].legend(fontsize=9)
	t_uv=np.arange(fl)*(1000.0/fs)
	axs[1,0].plot(t_uv,frame_uv/np.max(np.abs(frame_uv)),color='#7F7F7F')
	axs[1,0].set_title("KHUNG VO THANH / LANG (UNVOICED) - KHONG TUAN HOAN",fontsize=11,fontweight='bold')
	axs[1,0].set_xlabel("Thoi gian (ms)",fontsize=9)
	axs[1,0].set_ylabel("Bien do",fontsize=9)
	axs[1,0].grid(True)
	axs[1,1].plot(quef_ms[q_idx],cep_uv[q_idx],color='#7F7F7F',linewidth=1.5,label='Cepstrum')
	axs[1,1].set_title(f"CEPSTRUM KHUNG VO THANH (Phang ly, Prominence={prom_uv:.2f} < 3.90)",fontsize=11,fontweight='bold')
	axs[1,1].set_xlabel("Quefrency (ms)",fontsize=9)
	axs[1,1].set_ylabel("Bien do Cepstrum",fontsize=9)
	axs[1,1].grid(True)
	axs[1,1].legend(fontsize=9)
	plt.tight_layout()
	out_path=os.path.join(FIG_DIR,"voiced_vs_unvoiced_cepstrum.png")
	plt.savefig(out_path)
	plt.close()
	print(f"Generated: {out_path}")
def main():
	generate_test_contours(3.90)
	generate_voiced_vs_unvoiced()
if __name__=='__main__':
	main()

