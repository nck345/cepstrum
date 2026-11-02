import os
import numpy as np
import scipy.io.wavfile as wav
import scipy.signal as signal
def read_lab(lab_path):
	f0_mean,f0_std,f0_num=None,None,None
	segments=[]
	if not os.path.exists(lab_path):
		return f0_mean,f0_std,f0_num,segments
	with open(lab_path,'r',encoding='utf-8',errors='ignore') as f:
		for line in f:
			parts=line.strip().split()
			if not parts:
				continue
			k=parts[0].lower()
			if 'mean' in k:
				f0_mean=float(parts[1])
			elif 'std' in k:
				f0_std=float(parts[1])
			elif 'num' in k or 'count' in k:
				f0_num=float(parts[1])
			elif len(parts)>=3:
				segments.append((float(parts[0]),float(parts[1]),parts[2].lower()))
	return f0_mean,f0_std,f0_num,segments
def get_label_at_time(t,segments):
	for start,end,label in segments:
		if start<=t<=end:
			return label
	return 'sil'
def compute_frame_cepstrum(frame,fs,k_min,k_max,n_fft=2048):
	frame=frame-np.mean(frame)
	w_frame=frame*np.hamming(len(frame))
	spec=np.abs(np.fft.rfft(w_frame,n=n_fft))
	log_spec=np.log(spec+1e-12)
	cep=np.fft.irfft(log_spec,n=n_fft)
	sub=cep[k_min:k_max+1]
	best_idx=np.argmax(sub)
	best_k=k_min+best_idx
	c_max=sub[best_idx]
	bg_mean=np.mean(sub)
	bg_std=np.std(sub)+1e-12
	prom=(c_max-bg_mean)/bg_std
	return best_k,c_max,prom,cep
def extract_cepstrum_features(data,fs,frame_len_ms=30.0,hop_len_ms=10.0,f0_min=70.0,f0_max=400.0,energy_gate=0.02):
	if data.ndim>1:
		data=data[:,0]
	data=data.astype(np.float32)
	max_amp=np.max(np.abs(data))
	if max_amp>0:
		data=data/max_amp
	fl=int(round(frame_len_ms*1e-3*fs))
	hl=int(round(hop_len_ms*1e-3*fs))
	k_min=int(round(fs/f0_max))
	k_max=int(round(fs/f0_min))
	n_fft=2048 if fl<=2048 else 4096
	num_frames=(len(data)-fl)//hl+1
	time_axis=(np.arange(num_frames)*hl+fl/2.0)/fs
	proms=np.zeros(num_frames)
	k_stars=np.zeros(num_frames,dtype=int)
	c_maxs=np.zeros(num_frames)
	energies=np.zeros(num_frames)
	for i in range(num_frames):
		frame=data[i*hl:i*hl+fl]
		eng=np.sqrt(np.mean(frame**2))
		energies[i]=eng
		if eng<energy_gate:
			proms[i]=0.0
			k_stars[i]=k_min
			c_maxs[i]=0.0
			continue
		best_k,c_max,prom,_=compute_frame_cepstrum(frame,fs,k_min,k_max,n_fft)
		proms[i]=prom
		k_stars[i]=best_k
		c_maxs[i]=c_max
	return time_axis,proms,k_stars,c_maxs,energies,k_min,k_max
def otsu_unsupervised_threshold(values,num_bins=100):
	valid=values[values>0]
	if len(valid)==0:
		return 3.5
	hist,bin_edges=np.histogram(valid,bins=num_bins)
	hist=hist.astype(float)/len(valid)
	bin_centers=(bin_edges[:-1]+bin_edges[1:])/2.0
	best_thresh=bin_centers[len(bin_centers)//2]
	max_var=0.0
	weight0=0.0
	sum0=0.0
	total_mean=np.sum(hist*bin_centers)
	for i in range(len(hist)):
		weight0+=hist[i]
		if weight0==0:
			continue
		weight1=1.0-weight0
		if weight1==0:
			break
		sum0+=hist[i]*bin_centers[i]
		mean0=sum0/weight0
		mean1=(total_mean-sum0)/weight1
		var_between=weight0*weight1*((mean0-mean1)**2)
		if var_between>max_var:
			max_var=var_between
			best_thresh=bin_centers[i]
	return float(best_thresh)
def predict_f0_cepstrum(wav_path,threshold=3.90,frame_len_ms=30.0,hop_len_ms=10.0,kernel_size=5):
	fs,data=wav.read(wav_path)
	time_axis,proms,k_stars,c_maxs,energies,k_min,k_max=extract_cepstrum_features(data,fs,frame_len_ms,hop_len_ms)
	f0_raw=np.where(proms>=threshold,fs/k_stars,0.0)
	f0_filtered=signal.medfilt(f0_raw,kernel_size=kernel_size)
	return fs,data,time_axis,f0_filtered,proms,energies
