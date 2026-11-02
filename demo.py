import os
import sys
sys.stdout.reconfigure(encoding='utf-8')
import glob
import json
import numpy as np
import scipy.io.wavfile as wav
import scipy.signal as signal
import matplotlib.pyplot as plt
from cepstrum_utils import read_lab,extract_cepstrum_features
BASE_DIR=os.path.dirname(os.path.abspath(__file__))
TEST_DIR=os.path.join(BASE_DIR,'TinHieuKiemThu')
CONFIG_PATH=os.path.join(BASE_DIR,'threshold_config.json')
FIG_DIR=os.path.join(BASE_DIR,'figures')
os.makedirs(FIG_DIR,exist_ok=True)
def main():
	test_path=sys.argv[1] if len(sys.argv)>1 else TEST_DIR
	t=3.90
	if os.path.exists(CONFIG_PATH):
		with open(CONFIG_PATH,'r',encoding='utf-8') as fp:
			cfg=json.load(fp)
			t=cfg.get("optimal_threshold",3.90)
	print("="*80)
	print("  CHUONG TRINH DEMO UOC LUONG F0 BANG THUAT TOAN CEPSTRUM (1 LAN CHAY)")
	print(f"  Nguong phan biet V/UV toi uu (Hoc khong giam sat): T* = {t:.2f}")
	print("="*80)
	wav_files=sorted(glob.glob(os.path.join(test_path,'*.wav')))
	if not wav_files:
		print("Khong tim thay file wav trong:",test_path)
		return
	fig,axs=plt.subplots(len(wav_files),2,figsize=(14,3.2*len(wav_files)),dpi=120)
	scores=[]
	for idx,wav_file in enumerate(wav_files):
		bname=os.path.basename(wav_file)
		lab_file=os.path.splitext(wav_file)[0]+'.lab'
		gt_mean,gt_std,gt_num,_=read_lab(lab_file)
		fs,data=wav.read(wav_file)
		if data.ndim>1:
			data=data[:,0]
		data=data.astype(np.float32)
		dur=len(data)/fs
		time_signal=np.linspace(0,dur,len(data))
		time_axis,proms,k_stars,c_maxs,energies,k_min,k_max=extract_cepstrum_features(data,fs)
		f0_raw=np.where(proms>=t,fs/k_stars,0.0)
		f0_med=signal.medfilt(f0_raw,kernel_size=5)
		v=f0_med[f0_med>0]
		p_mean=float(np.mean(v)) if len(v)>0 else 0.0
		p_std=float(np.std(v)) if len(v)>0 else 0.0
		p_num=len(v)
		m_mean=abs(p_mean-gt_mean)/gt_mean*100.0 if gt_mean else 0.0
		m_std=abs(p_std-gt_std)/gt_std*100.0 if gt_std else 0.0
		m_num=abs(p_num-gt_num)/gt_num*100.0 if gt_num else 0.0
		f_score=(m_mean+m_std+m_num)/3.0
		scores.append(f_score)
		ax1=axs[idx,0]
		ax2=axs[idx,1]
		ax1.plot(time_signal,data/np.max(np.abs(data)),color='#2B5B84',linewidth=0.7)
		ax1.set_title(f"{bname} - Waveform",fontsize=10,fontweight='bold')
		ax1.set_ylabel("Bien do",fontsize=9)
		ax1.grid(True,linestyle='--',alpha=0.5)
		f0_plot=np.where(f0_med>0,f0_med,np.nan)
		ax2.scatter(time_axis,f0_plot,color='#D9381E',s=8,label=f'Pred: Mean={p_mean:.1f}Hz, Std={p_std:.1f}Hz, N={p_num}')
		if gt_mean:
			ax2.axhline(gt_mean,color='#2CA02C',linestyle='--',linewidth=1.5,label=f'GT: Mean={gt_mean:.1f}Hz, Std={gt_std:.1f}Hz, N={int(gt_num)}')
		ax2.set_title(f"{bname} - F0 Contour (Score MAPE={f_score:.2f}%)",fontsize=10,fontweight='bold')
		ax2.set_ylabel("F0 (Hz)",fontsize=9)
		ax2.set_ylim(50,450)
		ax2.grid(True,linestyle='--',alpha=0.5)
		ax2.legend(loc='upper right',fontsize=8)
		print(f"[{idx+1}/4] {bname:<16} | MAPE_mean={m_mean:5.2f}% | MAPE_std={m_std:5.2f}% | MAPE_num={m_num:5.2f}% | Score={f_score:5.2f}%")
	plt.tight_layout()
	demo_fig=os.path.join(FIG_DIR,'demo_all_test_signals.png')
	plt.savefig(demo_fig)
	avg_err=float(np.mean(scores))
	final_acc=100.0-avg_err
	print("-"*80)
	print(f"KET QUA CHUNG CUOC: Sai so trung binh = {avg_err:.2f}% | FINAL SCORE = {final_acc:.2f}% ({final_acc/10:.2f}/10)")
	print(f"Da xuat anh tong hop tai: {demo_fig}")
	print("="*80)
if __name__=='__main__':
	main()
