# HƯỚNG DẪN THUYẾT TRÌNH BẢO VỆ BÀI TẬP LỚN 2: THUẬT TOÁN CEPSTRUM & PHÂN NGƯỠNG HỌC KHÔNG GIÁM SÁT

---

## TỔNG QUAN PHẦN THUYẾT TRÌNH
- **Học phần:** Xử Lý Tiếng Nói
- **Sinh viên thực hiện:** Nguyễn Chánh Khiêm | **MSSV:** 102230299 | **Lớp:** 23T_DT3
- **Chuyên đề đảm nhiệm:** Ước lượng Tần số cơ bản $F_0$ bằng Thuật toán Cepstrum trên miền Quefrency và Tìm ngưỡng tối ưu Voiced/Unvoiced bằng Học không giám sát (Histogram 50/50 & Otsu).
- **Vị trí slide:** Từ **Slide 28** đến **Slide 36** trong tệp trình chiếu `XLTN_STE+ZCR.pptx`.
- **Thời lượng khuyến nghị:** 7 - 9 phút (khoảng 45 - 60 giây mỗi slide).

---

## KỊCH BẢN THUYẾT TRÌNH CHI TIẾT TỪNG SLIDE (SLIDE-BY-SLIDE SCRIPT)

### SLIDE 28: TRANG BÌA CHUYÊN ĐỀ
- **Nội dung hiển thị:** Tiêu đề bài tập, tên chuyên đề, thông tin sinh viên thực hiện.
- **Thời lượng:** 30 giây.
- **Lời thoại trình bày:**
  > *"Kính thưa thầy, tiếp nối phần trình bày của hai bạn về thuật toán ACF và AMDF trên miền thời gian, em xin phép đại diện nhóm trình bày phần nghiên cứu chuyên sâu thứ ba: **Ước lượng tần số cơ bản F0 bằng thuật toán Cepstrum trên miền Quefrency**, kết hợp **giải pháp tìm ngưỡng tối ưu phân biệt Hữu thanh / Vô thanh bằng phương pháp học không giám sát** dựa trên phân bố Histogram với giả định tỉ lệ 50/50. Em là Nguyễn Chánh Khiêm, sinh viên lớp 23T_DT3."*

---

### SLIDE 29: NỘI DUNG CHÍNH (AGENDA)
- **Nội dung hiển thị:** 6 mục chính từ so sánh thuật toán, cơ sở lý thuyết, minh họa khung âm thanh, giải pháp phân ngưỡng, kết quả số liệu thực nghiệm đến đồ thị F0 contour.
- **Thời lượng:** 30 giây.
- **Lời thoại trình bày:**
  > *"Bài báo cáo của em gồm 6 nội dung trọng tâm:
  > 1. Đối chiếu và so sánh ưu nhược điểm của 3 thuật toán ACF, AMDF và Cepstrum.
  > 2. Cơ sở toán học của thuật toán Cepstrum trên miền Quefrency.
  > 3. Minh họa trực quan sự khác biệt giữa khung Hữu thanh và Vô thanh.
  > 4. Giải pháp phân ngưỡng tối ưu Voiced/Unvoiced bằng học không giám sát.
  > 5. Bảng số liệu đánh giá định lượng sai số MAPE trên tập kiểm thử độc lập.
  > 6. Trực quan hóa đường bao F0 contour đồng bộ với tín hiệu âm thanh."*

---

### SLIDE 30: SO SÁNH 3 THUẬT TOÁN: ACF VS AMDF VS CEPSTRUM
- **Nội dung hiển thị:** Bảng so sánh 6 tiêu chí kỹ thuật giữa ACF, AMDF và Cepstrum.
- **Thời lượng:** 60 - 75 giây.
- **Từ khóa cần nhấn mạnh:** *Bẫy Formant (Formant trap), Giải chập đồng cấu, Miễn nhiễm với Formant.*
- **Lời thoại trình bày:**
  > *"Thưa thầy, trên slide là bảng đối chiếu trực tiếp 3 thuật toán tìm F0:
  > - **ACF:** Làm việc trên miền thời gian, dựa vào tích phân chập tự nhân để tìm đỉnh cực đại $R_{\max}$. ACF kháng nhiễu trắng rất tốt nhưng điểm yếu chí mạng là **rất dễ bị bẫy bởi Formant thứ nhất ($F_1$)** của thanh đạo. Khi $F_1$ có năng lượng lớn, đồ thị ACF sẽ xuất hiện các đỉnh phụ cao hơn cả đỉnh chu kỳ thật, dẫn đến việc bắt nhầm chu kỳ của Formant.
  > - **AMDF:** Cũng trên miền thời gian, sử dụng tổng hiệu biên độ để tìm đáy cực tiểu $D_{\min}$. Thuật toán này không cần phép nhân nên tính toán rất nhẹ, nhưng nhạy cảm với nhiễu và rất dễ bắt nhầm đáy giả ở vùng trễ nhỏ.
  > - **Cepstrum:** Khác biệt hoàn toàn khi chuyển tín hiệu sang **miền Quefrency** thông qua kỹ thuật giải chập đồng cấu. Ưu điểm vượt trội nhất của Cepstrum so với ACF và AMDF là **hoàn toàn miễn nhiễm với Formant thanh đạo**. Thuật toán tách rời hoàn toàn xung kích thích của dây thanh ra khỏi khoang miệng, giúp việc định vị chu kỳ cơ bản $T_0$ đạt độ tin cậy tuyệt đối."*

---

### SLIDE 31: CƠ SỞ LÝ THUYẾT THUẬT TOÁN CEPSTRUM TRÊN MIỀN QUEFRENCY
- **Nội dung hiển thị:** Mô hình nguồn âm - bộ lọc ($s = e * h$), chuỗi 4 bước biến đổi (Hamming $\rightarrow$ FFT $\rightarrow$ Log $\rightarrow$ IFFT) và ý nghĩa trục Quefrency.
- **Thời lượng:** 75 - 90 giây.
- **Từ khóa cần nhấn mạnh:** *Tích chập biến thành tích nhân, tích nhân biến thành phép cộng, phân tách không gian quefrency.*
- **Lời thoại trình bày:**
  > *"Về cơ sở lý thuyết, tiếng nói được mô hình hóa bằng tích chập giữa xung kích thích dây thanh $e(n)$ và đáp ứng khoang miệng thanh đạo $h(n)$: $s(n) = e(n) * h(n)$. Vì bị dính qua phép tích chập, các bộ lọc tuyến tính thông thường không thể tách chúng ra được. Thuật toán Cepstrum thực hiện chuỗi 4 bước giải chập đồng cấu:
  > 1. Nhân cửa sổ Hamming và đệm số 0 lên kích thước lũy thừa 2 ($N_{\text{FFT}} = 2048$ hoặc $4096$).
  > 2. Biến đổi Fourier nhanh lần 1 (FFT): Phép tích chập biến thành phép nhân trên phổ tần số: $X(k) = E(k) \cdot H(k)$.
  > 3. Lấy phổ độ lớn và hàm Logarit tự nhiên: Phép nhân biến thành phép cộng: $\log |X(k)| = \log |E(k)| + \log |H(k)|$. Ở đây, đường bao Formant biến thiên chậm, còn các vạch họa âm dây thanh biến thiên tuần hoàn rất nhanh theo tần số.
  > 4. Biến đổi Fourier ngược lần 2 (IFFT): Chuyển sang miền Quefrency: $c(n) = c_e(n) + c_h(n)$.
  > 
  > Điểm mấu chốt nằm ở **sự phân tách không gian trên trục Quefrency**:
  > - Toàn bộ các đỉnh Formants biến thiên chậm ở phổ sẽ co cụm vào **vùng quefrency thấp dưới $2.5\text{ ms}$**.
  > - Chuỗi vạch họa âm tuần hoàn cách nhau $F_0$ trên phổ sẽ hội tụ thành **một đỉnh xung nhọn hoắt duy nhất** đứng tại vị trí chu kỳ cơ bản $k^* = T_0 \cdot F_s$ trong vùng quefrency cao từ $2.5\text{ ms}$ đến $14.3\text{ ms}$ (tương ứng dải sinh lý $70 - 400\text{ Hz}$). Từ đó ta tính được tần số cơ bản: $F_0 = F_s / k^*$."*

---

### SLIDE 32: MINH HỌA KHUNG HỮU THANH (VOICED) VS VÔ THANH (UNVOICED)
- **Nội dung hiển thị:** Đồ thị 4 ô so sánh dạng sóng thời gian và đồ thị Cepstrum của khung Hữu thanh vs Vô thanh từ file `phone_F1.wav`.
- **Thời lượng:** 60 giây.
- **Chỉ tay vào màn hình:** Chỉ vào đỉnh nhọn ở nửa trên và đường phẳng ở nửa dưới.
- **Lời thoại trình bày:**
  > *"Trên slide là hình ảnh kiểm chứng thực tế giữa 2 khung tín hiệu trích từ dữ liệu huấn luyện:
  > - **Ở nửa trên (Khung Hữu thanh):** Dạng sóng dao động tuần hoàn rõ rệt. Đồ thị Cepstrum trong dải quefrency xuất hiện một đỉnh xung cực kỳ sắc nhọn tại $T_0 = 4.69\text{ ms}$, tương ứng tần số $F_0 = 213.3\text{ Hz}$. Chỉ số độ nổi bật của đỉnh (Prominence Z-score) đạt $7.78$, vượt xa ngưỡng phân biệt.
  > - **Ở nửa dưới (Khung Vô thanh):** Dạng sóng ngẫu nhiên không có tính tuần hoàn. Phổ quefrency hoàn toàn phẳng lỳ, không có bất kỳ đỉnh nào nhô lên, chỉ số Prominence chỉ đạt $2.45$, thấp hơn ngưỡng. Do đó khung được kết luận là vô thanh và gán $F_0 = 0$."*

---

### SLIDE 33: GIẢI PHÁP TÌM NGƯỠNG TỐI ƯU HỌC KHÔNG GIÁM SÁT (50/50 HISTOGRAM)
- **Nội dung hiển thị:** Biểu đồ Histogram 2 đỉnh (Bimodal Distribution), đường làm mịn KDE, vị trí 2 đỉnh $M_1, M_2$ và ngưỡng cắt tối ưu $T^* = 3.90$.
- **Thời lượng:** 75 - 90 giây.
- **Từ khóa cần nhấn mạnh:** *Không giám sát (Unsupervised), Giả định 50/50, Phân bố 2 đỉnh (Bimodal), Đáy thung lũng Otsu.*
- **Lời thoại trình bày:**
  > *"Tiếp theo là phần giải quyết yêu cầu quan trọng nhất của đề bài: **Tìm ngưỡng tối ưu Voiced/Unvoiced bằng thuật toán học không giám sát**.
  > Trong thực tế, dữ liệu âm thanh thu vào không hề có nhãn ground-truth để biết trước khung nào là V hay UV. Vì vậy, ta phải để thuật toán tự khai phá phân bố dữ liệu tự nhiên của tín hiệu:
  > - Trong lời nói tự nhiên, tỉ lệ giữa các âm hữu thanh và các âm vô thanh hoặc khoảng lặng **xấp xỉ cân bằng 50% - 50%**.
  > - Khi ta trích xuất chỉ số Prominence của toàn bộ các khung và vẽ biểu đồ tần suất (Histogram), dữ liệu tự động tách thành **hai quả đồi phân bố rõ rệt (dạng hai đỉnh - Bimodal Distribution)**:
  >   + Đỉnh thứ nhất ($M_1 \approx 3.25$): Tập trung cụm các khung vô thanh và khoảng lặng.
  >   + Đỉnh thứ hai ($M_2 \approx 5.85$): Tập trung cụm các khung hữu thanh tuần hoàn.
  > - Ranh giới phân chia tối ưu tự nhiên nằm đúng tại **vùng trũng (thung lũng) ngăn cách giữa hai đỉnh**. Áp dụng thuật toán Otsu tối đa hóa phương sai liên nhóm và công thức trung điểm Giannakopoulos $T = (M_1 + M_2)/2$, hệ thống tự động xác định được ngưỡng tối ưu khoa học là **$T^* = 3.90$** mà không cần bất kỳ sự can thiệp thủ công nào."*

---

### SLIDE 34: KẾT QUẢ THỰC NGHIỆM ĐỊNH LƯỢNG TRÊN 4 FILE KIỂM THỬ
- **Nội dung hiển thị:** Bảng chi tiết 3 chỉ số MAPE cho 4 file test (`phone_F2`, `phone_M2`, `studio_F2`, `studio_M2`) và Final Score.
- **Thời lượng:** 60 giây.
- **Lời thoại trình bày:**
  > *"Sau khi xác định ngưỡng cố định $T^* = 3.90$, em khóa bộ tham số và đưa sang đánh giá kiểm chứng độc lập trên toàn bộ 4 file kiểm thử (`TinHieuKiemThu`). Kết quả đạt được như sau:
  > - Sai số tần số trung bình $\text{MAPE}_{\text{mean}}$ cực kỳ thấp: `phone_F2` chỉ lệch $2.46\%$, `phone_M2` lệch $0.40\%$, `studio_F2` lệch $1.28\%$, và `studio_M2` lệch $2.27\%$. Trung bình toàn bộ chỉ lệch **$1.60\%$** so với nhãn chuẩn của thầy.
  > - Sai số độ lệch chuẩn $\text{MAPE}_{\text{std}}$ trung bình là $5.85\%$.
  > - Sai số số lượng khung $\text{MAPE}_{\text{num}}$ trung bình là $24.28\%$.
  > 
  > Tổng hợp cả 3 tiêu chí theo đúng barem chấm điểm của môn học, sai số MAPE trung bình toàn tập test là **$10.58\%$**, tương ứng với **FINAL SCORE đạt $89.42\%$ (tức 8.94 trên thang điểm 10)**."*

---

### SLIDE 35: ĐỒ THỊ WAVEFORM & F0 CONTOUR TRÊN 4 FILE KIỂM THỬ
- **Nội dung hiển thị:** Hình ảnh tổng hợp cả 4 file test thể hiện dạng sóng âm thanh và các chấm đỏ $F_0$ bám sát đường nét đứt xanh lá ground-truth.
- **Thời lượng:** 45 giây.
- **Lời thoại trình bày:**
  > *"Đây là đồ thị trực quan hóa kết quả chạy 1 lần duy nhất trên toàn bộ 4 file kiểm thử theo đúng yêu cầu của thầy:
  > - Cột bên trái là dạng sóng âm thanh Waveform.
  > - Cột bên phải là đường bao tần số cơ bản F0 contour được biểu diễn bằng các chấm đỏ, so khớp với đường chuẩn ground-truth nét đứt màu xanh lá cây lấy từ file `.lab`.
  > - Ta thấy các chấm $F_0$ bám khít hoàn hảo vào đường chuẩn. Các gai đột biến (spikes) do hiện tượng nhân đôi chu kỳ đã được bộ lọc trung vị bậc 5 triệt tiêu hoàn toàn, tạo nên một đường contour rất mượt mà và chính xác."*

---

### SLIDE 36: KẾT LUẬN & ĐÁNH GIÁ HIỆU NĂNG
- **Nội dung hiển thị:** 4 gạch đầu dòng tổng kết các ưu thế của phương pháp Cepstrum và học không giám sát.
- **Thời lượng:** 30 - 45 giây.
- **Lời thoại trình bày:**
  > *"Tóm lại, qua quá trình nghiên cứu và thực nghiệm, em xin rút ra 4 kết luận chính:
  > 1. Thuật toán Cepstrum giải quyết triệt để hạn chế bẫy Formant của các phương pháp miền thời gian (ACF, AMDF).
  > 2. Giải pháp phân ngưỡng học không giám sát dựa trên phân bố 50/50 Histogram và Otsu hoạt động hoàn toàn tự động, khoa học và không cần dữ liệu có nhãn.
  > 3. Độ chính xác tần số trung bình đạt mức rất cao với sai số chỉ 1.60%, Final Score đạt 89.42%.
  > 4. Toàn bộ pipeline đã được vector hóa và đẩy mã nguồn lên GitHub sẵn sàng chạy thử nghiệm.
  > Em xin chân thành cảm ơn thầy và các bạn đã lắng nghe!"*

---

## BỘ CÂU HỎI VẤN ĐÁP CỦA GIẢNG VIÊN & HƯỚNG DẪN TRẢ LỜI ĐẠT ĐIỂM TỐI ĐA

### Câu hỏi 1: *"Tại sao em lại chọn Cepstrum? Nó có ưu điểm gì thực sự vượt trội so với ACF và AMDF?"*
- **Trả lời trực tiếp:**
  > *"Dạ thưa thầy, ưu điểm cốt lõi nhất của Cepstrum là **khả năng tách rời hoàn toàn nguồn kích thích dây thanh quản ra khỏi bộ lọc cộng hưởng khoang miệng (Formants)** bằng kỹ thuật giải chập đồng cấu. 
  > Trong ACF và AMDF, khi phát âm các nguyên âm có Formant thứ nhất ($F_1$) năng lượng lớn (từ $300 - 800\text{ Hz}$), dạng sóng thời gian bị dao động của Formant gối đè lên, tạo ra các đỉnh phụ cực đại trong ACF khiến thuật toán bắt nhầm tần số của Formant thay vì tần số dây thanh. 
  > Cepstrum đưa tín hiệu qua 2 lần biến đổi Fourier để chuyển về miền Quefrency, nơi các Formant bị dồn hết về vùng quefrency thấp ($< 2.5\text{ ms}$), còn chu kỳ dây thanh đứng độc lập ở vùng quefrency cao. Do đó Cepstrum hoàn toàn không bị bẫy bởi Formant."*

---

### Câu hỏi 2: *"Quefrency là gì? Tại sao qua FFT rồi IFFT thì đỉnh tìm được lại là chu kỳ $T_0$ chứ không phải tần số $F_0$?"*
- **Trả lời trực tiếp:**
  > *"Dạ thưa thầy:
  > 1. Tên gọi **Quefrency** là phép đảo chữ của Frequency do các tác giả Bogert và Tukey đặt ra để chỉ biến số độc lập của miền Cepstrum. Thứ nguyên toán học của nó là nghịch đảo của tần số: $\frac{1}{\text{Hz}} = \text{giây}$, bản chất của nó là **thời gian**.
  > 2. Sở dĩ đỉnh tìm được là chu kỳ $T_0$ là vì: Khi dây thanh rung với tần số $F_0$, trên phổ logarit xuất hiện các vạch họa âm cách đều nhau đúng một khoảng tần số $\Delta f = F_0$. Sự cách đều tuần hoàn trên trục tần số này đóng vai trò như một tần số dao động của phổ. Khi lấy biến đổi Fourier ngược (IFFT) của phổ logarit, theo định lý Fourier, một thành phần tuần hoàn theo tần số với chu kỳ $\Delta f$ sẽ biến thành một đỉnh xung nhọn tại vị trí nghịch đảo: $t = \frac{1}{\Delta f} = \frac{1}{F_0} = T_0$. 
  > Vì vậy, vị trí mẫu đỉnh $k^*$ chính là chu kỳ lấy mẫu, và ta tính được tần số cơ bản bằng cách lấy nghịch đảo: $F_0 = F_s / k^*$."*

---

### Câu hỏi 3: *"Tại sao em lại dùng thuật toán học không giám sát mà không dùng nhãn ground-truth trong file `.lab` để train?"*
- **Trả lời trực tiếp:**
  > *"Dạ thưa thầy, trong bài toán thực tế ngoài đời sống, bất kỳ đoạn thoại nào người dùng nói vào hệ thống đều là tín hiệu mới, hoàn toàn chưa có ai gán nhãn `.lab` trước. Nếu thuật toán bắt buộc phải có nhãn để tối ưu thì sẽ không thể ứng dụng được trên thực tế.
  > Thuật toán học không giám sát (Unsupervised Learning) phân tích trực tiếp hình dạng phân bố Histogram của các giá trị đặc trưng tuần hoàn của chính tín hiệu đó. Hệ thống tự động nhận biết đâu là vùng phân bố của vô thanh, đâu là vùng của hữu thanh và tự động tìm ra đường cắt tối ưu ở đáy thung lũng, giúp hệ thống hoạt động hoàn toàn tự thích nghi với mọi môi trường ghi âm."*

---

### Câu hỏi 4: *"Giải thích ý nghĩa của giả định tỉ lệ 50/50? Giả định này giúp ích gì cho thuật toán Histogram và Otsu?"*
- **Trả lời trực tiếp:**
  > *"Dạ thưa thầy:
  > 1. Về mặt âm học, tiếng nói tự nhiên của con người là sự đan xen giữa các âm hữu thanh (nguyên âm, phụ âm hữu thanh) với các âm vô thanh (phụ âm xát, tắc) và các khoảng ngắt nghỉ giữa các từ. Qua khảo sát thực nghiệm trên cả tập train và tập test, số khung hữu thanh chiếm từ $45\% - 49\%$, xấp xỉ tỉ lệ $50/50$.
  > 2. Ý nghĩa đối với thuật toán: Khi tỉ lệ hai nhóm xấp xỉ 50/50, biểu đồ tần suất (Histogram) của đặc trưng Prominence sẽ tạo thành **hai quả đồi có diện tích tương đương nhau** (phân bố hai đỉnh - Bimodal). Điều này đảm bảo giữa hai quả đồi luôn tồn tại một thung lũng rất sâu và rõ nét. Thuật toán Otsu dựa trên việc tối đa hóa phương sai giữa hai nhóm: $\sigma_B^2 = \omega_0 \omega_1 (\mu_0 - \mu_1)^2$, khi $\omega_0 \approx \omega_1 \approx 0.5$, tích $\omega_0 \omega_1$ đạt cực đại, giúp thuật toán Otsu hội tụ cực kỳ chính xác vào đáy thung lũng phân cách, cho ra ngưỡng phân biệt tối ưu $T^* = 3.90$."*

---

### Câu hỏi 5: *"Tại sao ở vùng Quefrency thấp ($< 2.5\text{ ms}$) em lại bắt buộc phải bỏ qua mà không tìm đỉnh ở đó?"*
- **Trả lời trực tiếp:**
  > *"Dạ thưa thầy, vùng quefrency thấp ($< 2.5\text{ ms}$, tương ứng với 40 mẫu đầu tiên ở tần số lấy mẫu $16\text{ kHz}$) là nơi tập trung toàn bộ năng lượng của bộ lọc thanh đạo $h(n)$ và các đỉnh cộng hưởng Formant. Ở vùng này, biên độ Cepstrum luôn rất lớn và dốc xuống từ gốc tọa độ. Nếu không giới hạn tìm kiếm từ $k_{\min} = 40$ mẫu trở đi, thuật toán sẽ luôn bắt nhầm vào các đỉnh của Formant ở quefrency thấp thay vì bắt đỉnh chu kỳ $T_0$ của dây thanh quản."*

---

### Câu hỏi 6: *"Khi gặp các khung khoảng lặng (Silence), thuật toán Cepstrum xử lý như thế nào để không bị sai?"*
- **Trả lời trực tiếp:**
  > *"Dạ thưa thầy, trong các khung khoảng lặng, tín hiệu chỉ là nhiễu nền rất nhỏ. Vì Cepstrum lấy logarit biên độ $\log |X(k)|$, phép toán logarit có xu hướng nén dải động và khuếch đại nhiễu ngẫu nhiên ở mức biên độ cực nhỏ, khiến đồ thị Cepstrum của khoảng lặng đôi khi xuất hiện các gai nhiễu giả.
  > Để xử lý triệt để hiện tượng này, em áp dụng **kỹ thuật lọc năng lượng (Energy Gating)**: Trước khi tính Cepstrum, em tính năng lượng ngắn hạn (RMS) của khung. Nếu năng lượng khung nhỏ hơn ngưỡng khoảng lặng (nhỏ hơn $2\%$ năng lượng cực đại của file), em gán thẳng đặc trưng Prominence bằng $0$, triệt tiêu hoàn toàn khả năng nhận nhầm khoảng lặng thành hữu thanh."*

---

## HƯỚNG DẪN THỰC HÀNH LIVE DEMO TRƯỚC MẶT GIẢNG VIÊN

Nếu giảng viên yêu cầu: *"Em mở code lên chạy thử trực tiếp 1 lần cho thầy xem kết quả":*

1. **Bước 1: Mở Terminal (PowerShell hoặc Command Prompt) và di chuyển vào thư mục dự án:**
   ```powershell
   cd "cepstrum"
   ```

2. **Bước 2: Chạy file `demo.py` (Script chạy 1 lần duy nhất cho toàn bộ tập kiểm thử):**
   ```powershell
   python demo.py
   ```

3. **Bước 3: Thuyết minh nhanh kết quả xuất ra trên màn hình Terminal:**
   - Chỉ vào dòng kết quả của 4 file test:
     > *"Dạ thưa thầy, chương trình vừa chạy qua toàn bộ 4 file kiểm thử:
     > - Sai số tần số trung bình $F_{0\text{mean}}$ của cả 4 file đều dưới $2.5\%$, trong đó `phone_M2` chỉ lệch $0.40\%$.
     > - Sai số MAPE trung bình toàn bài là $10.58\%$, độ chính xác Final Score đạt **$89.42\%$**."*
   - Cửa sổ đồ thị tổng hợp `demo_all_test_signals.png` sẽ tự động hiển thị sóng âm và các chấm đỏ $F_0$ bám sát đường chuẩn xanh lá cây.

4. **Bước 4: Nếu thầy muốn xem bảng phân tích Histogram học không giám sát:**
   ```powershell
   python train_analysis.py
   ```
   - Chỉ vào đồ thị Histogram:
     > *"Dạ đây là đồ thị phân bố hai đỉnh thể hiện giả định 50/50 và vị trí ngưỡng tối ưu $T^* = 3.90$ nằm ở đáy thung lũng."*
