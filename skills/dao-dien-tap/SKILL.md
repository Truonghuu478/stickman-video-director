---
name: dao-dien-tap
description: Đạo diễn một tập phim hoạt hình đời thường không lời cho TikTok và Facebook Reels bằng core directing-stickman-videos. Gọi trống để tự chọn chuyện mới và xuất gói quay Google Flow, hoặc tiếp tục dựng một tập đã có clip.
---

# Đạo diễn một tập

Một lần gọi `$dao-dien-tap` tạo **đúng một tập độc lập**, mặc định khoảng 30 giây, dọc 9:16. Nếu người dùng đưa chủ đề, thời lượng hoặc ảnh thì dùng ngay. Nếu gọi trống, tự quyết các lựa chọn sáng tác và giao cả gói trong lượt đó. Viết kịch bản, chỉ dẫn dựng và caption đăng bài bằng tiếng Việt. Viết prompt ảnh và chuyển động bằng tiếng Anh.

## Dùng core của repo

Tìm thư mục thật của skill này (lần theo symlink), rồi mở [directing-stickman-videos](../directing-stickman-videos/SKILL.md) và [ranh giới các chế độ](../directing-stickman-videos/references/mode-execution-boundaries.md). Dùng nhánh **A · Director** làm cơ sở. Đọc và áp dụng các phần sau tại đúng bước:

- Khi viết storyboard, dùng [storyboard-template](../directing-stickman-videos/references/storyboard-template.md) cho mục đích từng cảnh, nhịp, bố cục và trạng thái chuyển cảnh. Dùng phần “Separate design, position and state” trong [cozy-storytelling](../directing-stickman-videos/references/cozy-storytelling.md) để theo dõi nhân vật và đạo cụ.
- Khi viết prompt, dùng [omni-flash-prompt-contract](../directing-stickman-videos/references/omni-flash-prompt-contract.md) cho prompt độc lập, khóa ngoại hình, khung mở/kết và hướng dẫn ghép. Khi chọn âm thanh, tra thư viện của core bằng `node scripts/audio-library.mjs search <keyword>` từ thư mục core.

Đây là cấu hình riêng cho yêu cầu “một lệnh, một tập, không lời”. Hoàn tất cả storyboard và prompt trong một lượt, chỉ dừng ở storyboard khi người dùng yêu cầu duyệt. Chuyển nhịp kể bằng VO của core thành hành động nhìn thấy được. Mỗi clip nguồn dài 4–10 giây. Giữ tạo hình theo ảnh người dùng và đổi địa điểm khi câu chuyện cần. Các lựa chọn này chỉ áp dụng khi gọi skill này.

## Chọn chuyện và đạo diễn

1. Lưu các tập ở `../stickman-video-projects/doi-thuong/` tính từ gốc repo. Đọc dòng **Dấu tập** trong các file `*/FLOW.md` trước khi chọn chuyện. Dòng này ghi *bối cảnh | điều nhân vật muốn | trở ngại | cách kết*. Nếu giống một tập cũ cả xung đột lẫn cách kết, chọn chuyện khác. Chủ đề có thể đến từ bất kỳ sinh hoạt nào. Một nhân vật có thể trở lại, nhưng người xem mới phải hiểu ngay tập này. Tạo thư mục mới theo ngày và tên ngắn, chọn hậu tố khác nếu đã tồn tại. Khi người dùng đưa clip hoặc nói “dựng tiếp”, mở lại đúng thư mục tập đã nêu hoặc tập đang làm trong hội thoại.
2. Chọn một khoảnh khắc đời thường mà người xem nhận ra qua một **hành vi cụ thể**. Viết chuyện thành một chuỗi nguyên nhân: nhân vật muốn gì → làm gì → việc đó dẫn tới chuyện gì → họ quyết định thế nào. Cho thấy dấu hiệu đầu tiên trong 1–2 giây. Cú kết phải trả lời tình huống đầu hoặc khiến một chi tiết cũ đổi nghĩa. Không bắt buộc có cú lật hay kết hài.
3. Chốt ngoại hình từ ảnh tham chiếu nếu có. Mặc định dùng nhân vật 2D trong brief ban đầu: tóc đen hơi rối, mặt tròn sáng, sơ mi xanh nhạt, quần xám, thắt lưng và giày đen. Sao nguyên mô tả tiếng Anh về ngoại hình vào mọi prompt có nhân vật đó. Nét mặt, tư thế, quần áo theo hoàn cảnh và đạo cụ có thể thay đổi khi kịch bản thể hiện được lý do. Nếu người dùng chỉ định bộ nhân vật khác, dùng bộ đó.
4. Với từng shot, chọn điều khán giả cần nhìn thấy rồi mới chọn cỡ cảnh. Toàn cảnh cho biết ai đứng đâu; trung cảnh thấy một quyết định qua bàn tay, vai, chân; cận cảnh cho thấy bằng chứng hoặc hậu quả. Một clip chứa một hành động chính và phản ứng vừa đủ. Mô tả động tác có thể diễn được thay cho nhãn cảm xúc. Giữ trục máy và hướng nhìn trong cùng không gian. Chỉ đổi góc khi góc mới tiết lộ điều gì hoặc theo tiếp hành động.
5. Thiết kế lý do tương tác từ chính câu chuyện: khoảnh khắc khiến người xem thương hoặc bật cười, chi tiết khiến họ nhớ đến một người để gửi, hoặc lựa chọn có hai cách hiểu để bàn luận. Chọn cách hợp tập. Caption đăng bài có thể hỏi một câu cụ thể sau cú kết. Xem riêng phần hình, bỏ cả tiêu đề, caption và tiếng: người xem phải chỉ ra được nhân vật muốn gì, điều gì vừa đổi và bằng chứng nằm ở shot nào. Nếu phải đọc lời giải thích mới hiểu, sửa hành động trước khi viết prompt.

## Gói bàn giao mỗi lần gọi

Viết **FLOW.md** vào thư mục tập. Mở đầu bằng tên, Dấu tập, tóm tắt và kịch bản không lời có mở–diễn biến–kết. Sau đó ghi khóa ngoại hình, tương quan vị trí và các đạo cụ cần theo dõi. Cho mỗi shot một mã S01, S02… và đủ thông tin để render riêng:

- Mốc vào/ra trên phim đã dựng; số giây cần tạo ở Flow; đoạn giữ lại trong clip nguồn. Tổng phần giữ lại bằng thời lượng bản dựng. Chọn thời lượng nguồn mà model hiện tại hỗ trợ trong khoảng 4–10 giây. Khi chưa biết lựa chọn của giao diện, ghi rõ giả định 8 giây của workflow hiện có và lập điểm cắt trong giới hạn đó. Chia đôi hành động nếu không đủ thời gian.
- Cỡ cảnh, vị trí máy, ai nhìn về đâu, trạng thái đầu → động tác/tiếp xúc → trạng thái cuối. Ở mỗi chỗ nối, ghi hành động hoặc ánh mắt dẫn sang cảnh sau và một chi tiết cần khớp (tay nào, hướng di chuyển, đạo cụ, vị trí). Nếu nhảy thời gian hoặc địa điểm, chỉ rõ dấu hiệu khán giả sẽ thấy.
- Một prompt ảnh **Start frame** và một prompt **Motion** hoàn chỉnh, mỗi prompt trong một khối riêng để dán. Start frame mô tả trạng thái ngay trước hành động, không tiết lộ trước cú kết. Motion nhắc lại ngoại hình đang thấy, bối cảnh, trục máy, chia nhịp theo giây thực trong clip và kết thúc ở tư thế cắt đã định. Yêu cầu diễn bằng cơ thể, không lời thoại, hát, nhép miệng, phụ đề hoặc chữ giải thích. Đặt chi tiết quyết định ở vùng dễ thấy trên màn hình dọc. Không dùng “same as previous shot” thay cho mô tả.
- Ghi tên ảnh/clip cần lưu, gợi ý SFX đúng lúc vật chạm hoặc nhân vật hành động, và chỗ nên để yên. Kết tài liệu bằng thứ tự ráp, caption dùng cho TikTok/Facebook Reels và chi tiết có thể làm ảnh bìa.

Ghi **cut.tsv** với bốn cột phân cách bằng tab: `clip`, `flow_s`, `in_s`, `out_s`. Mỗi dòng là một shot theo thứ tự dựng. Đường dẫn clip tính từ thư mục tập, ví dụ `clips/S01.mp4`. Mốc giây tính từ đầu clip nguồn. Chạy `python3 <skill>/scripts/cut.py <tập>/cut.tsv` rồi đối chiếu tổng thời lượng công cụ in ra với FLOW.md. Trước khi giao, đọc liền các khung cuối/đầu kề nhau, sửa các chỗ nhân vật đổi tay, đồ vật xuất hiện lại hoặc động tác bị diễn hai lần.

## Từ gói quay đến MP4

- Tận dụng [workflow Flow hiện có](../stickman-flow-pipeline/SKILL.md) cho thao tác tạo ảnh đầu, lưu clip và QC. Khi dùng tuyến tạo ảnh đã cấu hình và được phép, chạy [gen-frame.sh](../stickman-flow-pipeline/gen-frame.sh) với prompt từng shot và đường dẫn `flow-input/S01.png` tương ứng, rồi kiểm tra ảnh. Script này nhận văn bản. Nếu đã có ảnh chuẩn cần giữ nguyên, dùng ảnh đó trực tiếp cho shot có bố cục phù hợp. Nếu chỉ yêu cầu prompt hoặc dịch vụ ảnh chưa dùng được, giao đầy đủ prompt và ghi rõ ảnh nào còn thiếu.
- Ở Google Flow, dùng khung dọc, một đầu ra, ảnh cảnh tương ứng ở **Start frame**. Với shot tiếp diễn cùng góc, ưu tiên khung cắt thực tế của clip trước; khi đổi góc, dùng ảnh đầu mới giữ đúng trạng thái. Trong quy trình hiện có, người dùng tạo clip ở Flow rồi đặt vào `clips/`. Nếu có phiên Flow khả dụng và người dùng đã giao việc render trong phạm vi đó, dùng đúng thiết lập và lưu kết quả. Khi chỉ có gói quay, bàn giao link thư mục và vị trí đặt clip, không báo đã có MP4.
- Khi nhận clip, kiểm tra từng chuyển động chính và cặp khung ở điểm cắt. Dùng tên file thực trong cut.tsv, điều chỉnh in/out theo diễn xuất thực, rồi dựng bằng `python3 <skill>/scripts/cut.py <tập>/cut.tsv --render <tập>/picture.mp4`. Bản này dùng hình, bỏ audio nguồn để loại giọng phát sinh. Nếu tập có SFX, dùng thư viện core để đồng bộ tiếng theo cú chạm thực tế, giữ credit cần thiết và xuất bản mix riêng. Xem bản dựng ở tốc độ thường với tiếng tắt, kiểm tra file, thời lượng và các điểm nối trước khi giao. Báo rõ shot còn thiếu hoặc lỗi nhìn thấy. Bàn giao caption cùng phim; đăng bài là thao tác riêng của người dùng.
