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
def run_train_analysis():
	wav_files=sorted(glob.glob(os.path.join(TRAIN_DIR,'*.wav')))
	all_proms=[]
	train_data=[]
	for f in wav_files:
		lab_file=os.path.splitext(f)[0]+'.lab'
		gt_mean,gt_std,gt_num,_=read_lab(lab_file)
		fs,data=wav.read(f)
		time_axis,proms,k_stars,c_maxs,energies,k_min,k_max=extract_cepstrum_features(data,fs)
		all_proms.extend(proms.tolist())
		train_data.append((os.path.basename(f),fs,proms,k_stars,gt_mean,gt_std,gt_num))
	all_proms=np.array(all_proms)
	t_otsu=otsu_unsupervised_threshold(all_proms)
	hist,bin_edges=np.histogram(all_proms[all_proms>0],bins=60)
	bin_centers=(bin_edges[:-1]+bin_edges[1:])/2.0
	smoothed_hist=signal.medfilt(hist,5)
	peaks,_=signal.find_peaks(smoothed_hist,distance=8)
	if len(peaks)>=2:
		m1=bin_centers[peaks[0]]
		m2=bin_centers[peaks[1]]
		t_mid=(m1+m2)/2.0
	else:
		m1,m2=3.3,5.5
		t_mid=4.4
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
		"frame_len_ms":30.0,
		"hop_len_ms":10.0,
		"f0_min_hz":70.0,
		"f0_max_hz":400.0,
		"energy_gate_ratio":0.02,
		"unsupervised_otsu_threshold":round(t_otsu,2),
		"unsupervised_midpoint_threshold":round(t_mid,2),
		"optimal_threshold":round(best_t,2),
		"train_score_mape":round(min_score,2)
	}
	with open(CONFIG_PATH,'w',encoding='utf-8') as fp:
		json.dump(cfg,fp,indent=2)
	plt.figure(figsize=(10,6),dpi=150)
	plt.hist(all_proms[all_proms>0],bins=60,color='#4A90E2',alpha=0.6,edgecolor='black',density=True,label='Phan bo dac trung Cepstrum Prominence')
	plt.plot(bin_centers,smoothed_hist/np.sum(smoothed_hist*np.diff(bin_edges)[0]),color='#D0021B',linewidth=2.5,label='Duong cong mat do lam min (KDE/Filtered)')
	plt.axvline(best_t,color='#7ED321',linestyle='--',linewidth=2.5,label=f'Nguong toi uu T* = {best_t:.2f} (Train Score={min_score:.2f}%)')
	plt.axvline(t_mid,color='#F5A623',linestyle=':',linewidth=2.0,label=f'Trung diem 2 dinh (50/50 Midpoint) T = {t_mid:.2f}')
	plt.title('PHAN BO HISTOGRAM HOC KHONG GIAM SAT VA XAC DINH NGUONG V/UV (CEPSTRUM)',fontsize=13,fontweight='bold')
	plt.xlabel('Chi so dac trung tuan hoan Cepstrum (Peak Prominence Z-score)',fontsize=11)
	plt.ylabel('Mat do xac suat',fontsize=11)
	plt.grid(True,linestyle='--',alpha=0.5)
	plt.legend(fontsize=10)
	plt.tight_layout()
	out_fig=os.path.join(FIG_DIR,'unsupervised_histogram_analysis.png')
	plt.savefig(out_fig)
	plt.close()
	print(f"Train analysis done. Otsu={t_otsu:.2f}, Midpoint={t_mid:.2f}, Optimal T*={best_t:.2f}, Train Error={min_score:.2f}%")
if __name__=='__main__':
	run_train_analysis()

