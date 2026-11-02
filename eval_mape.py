import os
import sys
sys.stdout.reconfigure(encoding='utf-8')
import glob
import json
import numpy as np
import scipy.io.wavfile as wav
import scipy.signal as signal
from cepstrum_utils import read_lab,extract_cepstrum_features
BASE_DIR=os.path.dirname(os.path.abspath(__file__))
TRAIN_DIR=os.path.join(BASE_DIR,'TinHieuHuanLuyen_latest')
TEST_DIR=os.path.join(BASE_DIR,'TinHieuKiemThu')
CONFIG_PATH=os.path.join(BASE_DIR,'threshold_config.json')
def load_config():
	if os.path.exists(CONFIG_PATH):
		with open(CONFIG_PATH,'r',encoding='utf-8') as fp:
			return json.load(fp)
	return {"optimal_threshold":3.90}
def evaluate_folder(folder_path,threshold=3.90):
	wav_files=sorted(glob.glob(os.path.join(folder_path,'*.wav')))
	results=[]
	for wav_file in wav_files:
		base_name=os.path.basename(wav_file)
		lab_file=os.path.splitext(wav_file)[0]+'.lab'
		gt_mean,gt_std,gt_num,_=read_lab(lab_file)
		fs,data=wav.read(wav_file)
		time_axis,proms,k_stars,c_maxs,energies,k_min,k_max=extract_cepstrum_features(data,fs)
		f0_raw=np.where(proms>=threshold,fs/k_stars,0.0)
		f0_med=signal.medfilt(f0_raw,kernel_size=5)
		v=f0_med[f0_med>0]
		p_mean=float(np.mean(v)) if len(v)>0 else 0.0
		p_std=float(np.std(v)) if len(v)>0 else 0.0
		p_num=len(v)
		m_mean=abs(p_mean-gt_mean)/gt_mean*100.0 if gt_mean else 0.0
		m_std=abs(p_std-gt_std)/gt_std*100.0 if gt_std else 0.0
		m_num=abs(p_num-gt_num)/gt_num*100.0 if gt_num else 0.0
		file_score=(m_mean+m_std+m_num)/3.0
		results.append({
			'file':base_name,
			'gt_mean':gt_mean,'pred_mean':p_mean,'mape_mean':m_mean,
			'gt_std':gt_std,'pred_std':p_std,'mape_std':m_std,
			'gt_num':gt_num,'pred_num':p_num,'mape_num':m_num,
			'score':file_score
		})
	return results
def print_result_table(title,results):
	print("="*105)
	print(f"                               {title}")
	print("="*105)
	print(f"{'file':<18} | {'MAPE f0 mean (%)':<20} | {'MAPE f0 std (%)':<19} | {'MAPE f0 num (%)':<19} | {'average MAPE (%)':<20}")
	print("-"*105)
	all_sc=[]
	for r in results:
		f_name=r['file']
		m_mean=f"{r['mape_mean']:>18.2f} %"
		m_std=f"{r['mape_std']:>17.2f} %"
		m_num=f"{r['mape_num']:>17.2f} %"
		m_avg=f"{r['score']:>18.2f} %"
		all_sc.append(r['score'])
		print(f"{f_name:<18} | {m_mean} | {m_std} | {m_num} | {m_avg}")
	print("-"*105)
	final_avg=float(np.mean(all_sc))
	print(f"{'TỔNG CỘNG':<18} | {'':<20} | {'':<19} | {'':<19} | {final_avg:>18.2f} %")
	print("="*105)
	return final_avg
def main():
	train_path=sys.argv[1] if len(sys.argv)>1 else TRAIN_DIR
	test_path=sys.argv[2] if len(sys.argv)>2 else TEST_DIR
	cfg=load_config()
	t=cfg.get("optimal_threshold",3.90)
	print(f"\n>>> ĐANG ĐÁNH GIÁ THUẬT TOÁN CEPSTRUM VỚI NGƯỠNG TỐI ƯU T* = {t:.2f} <<<")
	res_train=evaluate_folder(train_path,t)
	train_avg=print_result_table("BẢNG 1: KẾT QUẢ ĐÁNH GIÁ TẬP HUẤN LUYỆN (CEPSTRUM)",res_train)
	res_test=evaluate_folder(test_path,t)
	test_avg=print_result_table("BẢNG 2: KẾT QUẢ ĐÁNH GIÁ TẬP KIỂM THỬ (CEPSTRUM)",res_test)
	final_score=100.0-test_avg
	print(f"\n>>> KẾT QUẢ CHUNG CUỘC TẬP KIỂM THỬ:")
	print(f"    - Sai số MAPE trung bình: {test_avg:.2f}%")
	print(f"    - FINAL_SCORE (Độ chính xác): {final_score:.2f}% (Thang điểm 10: {final_score/10:.2f} / 10)\n")
if __name__=='__main__':
	main()

