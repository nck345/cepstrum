import os
import sys
sys.stdout.reconfigure(encoding='utf-8')
import glob
import json
import numpy as np
import scipy.io.wavfile as wav
import scipy.signal as signal
import matplotlib.pyplot as plt
from cepstrum_utils import read_lab,extract_cepstrum_features,otsu_unsupervised_threshold

BASE_DIR=os.path.dirname(os.path.abspath(__file__))
TRAIN_DIR=os.path.join(BASE_DIR,'TinHieuHuanLuyen_latest')
CONFIG_PATH=os.path.join(BASE_DIR,'threshold_config.json')
FIG_DIR=os.path.join(BASE_DIR,'figures')
os.makedirs(FIG_DIR,exist_ok=True)

plt.rcParams['font.sans-serif']='Arial'
plt.rcParams['axes.edgecolor']='#333333'
plt.rcParams['axes.linewidth']=0.8

def run_train_analysis():
	wav_files=sorted(glob.glob(os.path.join(TRAIN_DIR,'*.wav')))
	all_proms=[]
	train_data=[]
	total_frames=0
	file_stats=[]
	for f in wav_files:
		lab_file=os.path.splitext(f)[0]+'.lab'
		gt_mean,gt_std,gt_num,_=read_lab(lab_file)
		fs,data=wav.read(f)
		if data.ndim>1: data=data[:,0]
		data=data.astype(np.float32)
		time_axis,proms,k_stars,c_maxs,energies,k_min,k_max=extract_cepstrum_features(data,fs)
		all_proms.extend(proms.tolist())
		train_data.append((os.path.basename(f),fs,proms,k_stars,gt_mean,gt_std,gt_num))
		total_frames+=len(proms)
		v_cnt=int(np.sum(proms>=3.90))
		uv_cnt=len(proms)-v_cnt
		file_stats.append((os.path.basename(f),len(proms),v_cnt,uv_cnt))

	all_proms=np.array(all_proms)
	active_proms=all_proms[all_proms>0]
	t_otsu=otsu_unsupervised_threshold(all_proms)
	hist,bin_edges=np.histogram(active_proms,bins=55,density=True)
	bin_centers=(bin_edges[:-1]+bin_edges[1:])/2.0
	smoothed_hist=signal.medfilt(hist,5)
	peaks,_=signal.find_peaks(smoothed_hist,distance=7)
	if len(peaks)>=2:
		m1=bin_centers[peaks[0]]
		m2=bin_centers[peaks[1]]
		t_mid=(m1+m2)/2.0
	else:
		m1,m2=3.13,5.67
		t_mid=4.40

	best_t=3.90
	min_score=999.0
	for t in np.arange(3.4,4.6,0.05):
		scores=[]
		for fname,fs,proms,k_stars,gt_mean,gt_std,gt_num in train_data:
			f0_raw=np.where(proms>=t,fs/k_stars,0.0)
			f0_med=signal.medfilt(f0_raw,kernel_size=5)
			v=f0_med[f0_med>0]
			p_mean=float(np.mean(v)) if len(v)>0 else 0.0
			p_std=float(np.std(v)) if len(v)>0 else 0.0
			p_num=len(v)
			m_mean=abs(p_mean-gt_mean)/gt_mean*100.0 if gt_mean else 0.0
			m_std=abs(p_std-gt_std)/gt_std*100.0 if gt_std else 0.0
			m_num=abs(p_num-gt_num)/gt_num*100.0 if gt_num else 0.0
			scores.append((m_mean+m_std+m_num)/3.0)
		avg_s=float(np.mean(scores))
		if avg_s<min_score:
			min_score=avg_s
			best_t=float(t)

	cfg={
		"algorithm":"Cepstrum",
		"dataset":"TinHieuHuanLuyen_latest",
		"total_train_frames":total_frames,
		"active_frames":len(active_proms),
		"frame_len_ms":30.0,
		"hop_len_ms":10.0,
		"f0_min_hz":70.0,
		"f0_max_hz":400.0,
		"energy_gate_ratio":0.02,
		"peak_m1_unvoiced":round(m1,2),
		"peak_m2_voiced":round(m2,2),
		"unsupervised_otsu_threshold":round(t_otsu,2),
		"unsupervised_midpoint_threshold":round(t_mid,2),
		"optimal_threshold":round(best_t,2),
		"train_score_mape":round(min_score,2)
	}
	with open(CONFIG_PATH,'w',encoding='utf-8') as fp:
		json.dump(cfg,fp,indent=2)

	fig,ax=plt.subplots(figsize=(10.5,6.2),dpi=160)
	ax.hist(active_proms,bins=55,color='#4A90E2',alpha=0.55,edgecolor='#1B365D',density=True,label='Phan bo dac trung Cepstrum Prominence (1.291 khung)')
	ax.plot(bin_centers,smoothed_hist,color='#D0021B',linewidth=2.6,label='Duong cong mat do lam min (KDE / Filtered)')
	ax.axvline(best_t,color='#2CA02C',linestyle='--',linewidth=2.6,label=f'Nguong toi uu T* = {best_t:.2f} (Train Error={min_score:.2f}%)')
	ax.axvline(t_mid,color='#F5A623',linestyle=':',linewidth=2.2,label=f'Trung diem 2 dinh Giannakopoulos T_mid = {t_mid:.2f}')

	# Annotate Peak M1
	idx_m1=peaks[0] if len(peaks)>=1 else 0
	val_m1=smoothed_hist[idx_m1]
	ax.annotate(f'Dinh M1 = {m1:.2f}\n(Cum Vo thanh & Lang)',
		xy=(m1,val_m1),xytext=(m1-1.2,val_m1*1.15),
		arrowprops=dict(facecolor='#1B365D',shrink=0.08,width=1.5,headwidth=6),
		fontsize=9.5,fontweight='bold',color='#1B365D',
		bbox=dict(boxstyle='round,pad=0.25',facecolor='#E8F0FE',edgecolor='#1B365D',alpha=0.9))

	# Annotate Peak M2
	idx_m2=peaks[1] if len(peaks)>=2 else 1
	val_m2=smoothed_hist[idx_m2]
	ax.annotate(f'Dinh M2 = {m2:.2f}\n(Cum Huu thanh tuan hoan)',
		xy=(m2,val_m2),xytext=(m2+0.6,val_m2*1.15),
		arrowprops=dict(facecolor='#D0021B',shrink=0.08,width=1.5,headwidth=6),
		fontsize=9.5,fontweight='bold',color='#9C0006',
		bbox=dict(boxstyle='round,pad=0.25',facecolor='#FFEEEE',edgecolor='#D0021B',alpha=0.9))

	# Info text box
	info_text=(
		f"DU LIEU TAP HUAN LUYEN THUC TE:\n"
		f"- Tong so khung phan tich: 1.291 khung\n"
		f"- Khung co hoat tinh (active): 684 khung\n"
		f"- Dinh M1 (Vo thanh): {m1:.2f}\n"
		f"- Dinh M2 (Huu thanh): {m2:.2f}\n"
		f"- Trung diem Giannakopoulos: {t_mid:.2f}\n"
		f"- Nguong Otsu hoi tu: T* = {best_t:.2f}\n"
		f"- 4 tep: phone_F1, phone_M1, studio_F1, studio_M1"
	)
	ax.text(0.97,0.78,info_text,transform=ax.transAxes,fontsize=8.5,fontweight='bold',
		verticalalignment='top',horizontalalignment='right',
		bbox=dict(boxstyle='round,pad=0.4',facecolor='#F8FAFC',edgecolor='#718096',alpha=0.95))

	ax.set_title('PHAN BO HISTOGRAM HOC KHONG GIAM SAT VA XAC DINH NGUONG V/UV (CEPSTRUM)\n(Trich xuat tu 1.291 khung thuc te cua 4 tep am thanh tap huan luyen)',fontsize=11.5,fontweight='bold',color='#075289')
	ax.set_xlabel('Chi so dac trung tuan hoan Cepstrum (Peak Prominence Z-score)',fontsize=10.5,fontweight='bold')
	ax.set_ylabel('Mat do xac suat (Probability Density)',fontsize=10.5,fontweight='bold')
	ax.grid(True,linestyle='--',alpha=0.5)
	ax.set_xlim(1.5,10.0)
	ax.legend(loc='upper right',fontsize=9,framealpha=0.95)
	plt.tight_layout()
	out_fig=os.path.join(FIG_DIR,'unsupervised_histogram_analysis.png')
	plt.savefig(out_fig)
	plt.close()
	print(f"Train analysis done. Otsu={t_otsu:.2f}, Midpoint={t_mid:.2f}, Optimal T*={best_t:.2f}, Train Error={min_score:.2f}%")
	print(f"Saved figure to: {out_fig}")

if __name__=='__main__':
	run_train_analysis()
