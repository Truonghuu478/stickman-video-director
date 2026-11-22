# Kế hoạch: Radar xu hướng TikTok cho `dao-dien-tap`

Ngày: 2026-11-22 · Trạng thái: chờ duyệt · Phạm vi: `skills/dao-dien-tap/` và thư mục tập ở `../stickman-video-projects/doi-thuong/`

## 1. Mục tiêu

Trước khi chọn chuyện, skill lấy xu hướng TikTok Việt Nam đang chạy, lọc ra cái **mượn được cho phim hoạt hình không lời**, rồi phân tích vì sao video gốc viral để áp vào kịch bản. Kết quả: tập mới bám trend thật thay vì đoán, nhưng vẫn giữ luật của skill (không lời, không chữ, không nhạc bản quyền, 20–30 giây).

Ngoài phạm vi: tự động đăng bài, tải video người khác, cào API nội bộ TikTok, đo hiệu quả sau đăng (để giai đoạn 3).

## 2. Hiện trạng nguồn dữ liệu (đã kiểm tra 2026-11-22)

| Nguồn | Lấy tự động được? | Dữ liệu có | Ghi chú |
|---|---|---|---|
| Endless radar `endless.app/radar/tiktok/vietnam` | **Có**, qua Exa web fetch | Top 30 video 24h: tiêu đề, lượt xem, like, hashtag, âm thanh | Nguồn chính. Cập nhật nhiều lần/ngày. Lẫn quảng cáo (Sting, Grab) cần lọc |
| Social Voice `socialvoice.buzz` | **Có**, qua Exa | Bảng xếp hạng tìm kiếm TikTok theo ngày, có nhóm chủ đề | Tốt để biết chủ đề, không có hành vi cụ thể |
| Báo tổng hợp trend tuần: Tuổi Trẻ, VTV, Advertising Vietnam | **Có**, qua Exa search hoặc 9Router web search | Mô tả trend, nguồn gốc, vì sao lan | Tốt nhất để phân tích "vì sao viral" |
| TikTok Creative Center | **Không**. Trang render bằng JS, crawl trả rỗng | Hashtag, bài hát, creator theo vùng | Chỉ dùng khi người dùng tự mở và dán vào |
| Lịch dịp lễ: 20/11, Noel, Tết, 14/2, mùa thi | Không cần fetch | Ngày cố định | Ghi tay một lần trong skill |

Công cụ đã có sẵn, **không cần cài thêm**: Exa MCP (`web_search_exa`, `web_fetch_exa`) và skill `9router-web-search` / `9router-web-fetch`.

### Mẫu dữ liệu đã lấy được tuần này

- **Hội Chó Xấu Việt Nam**: khoe thú cưng nhan sắc "khó đỡ". Mượn được.
- **"2020 đã là 6 năm trước"**: hoài niệm, so ảnh cũ và nay. Mượn được.
- **20/11 tri ân thầy cô** và **19/11 Quốc tế Đàn ông**: dịp lễ, hết hạn nhanh. Mượn được nếu đăng kịp.
- Video mèo "tròn iu" top 5 với 8,7 triệu view: xác nhận thú cưng vẫn là mảng mạnh.
- **Gangnam Style Trio**, các bản remix nhạc: dựa vào nhạc bản quyền và người thật nhảy. Loại.
- **Bicep Heart**, khoe số đo "check profile": cần người thật và chữ. Loại.

## 3. Quy trình đề xuất

Thêm **bước 0 "Quét xu hướng"** vào đầu phần "Chọn chuyện và đạo diễn" của `SKILL.md`. Không viết script mới. Agent tự gọi công cụ tìm kiếm đang có.

### Bước 0.1: Thu thập

1. Fetch Endless radar Việt Nam, lấy top 30 video 24h.
2. Search "xu hướng mạng xã hội tuần qua" giới hạn 7 ngày, đọc 2–3 bài tổng hợp từ báo.
3. Đối chiếu lịch dịp lễ trong 14 ngày tới.
4. Nếu người dùng dán link hoặc ảnh chụp Creative Center, dùng luôn.

Nếu cả hai nguồn chính đều lỗi, ghi rõ lỗi trong TRENDS.md rồi chọn chuyện theo danh sách vùng chủ đề có sẵn của skill. Không bịa trend.

### Bước 0.2: Lọc

Loại ngay các trend:

- Dựa vào **nhạc có bản quyền**, lời bài hát hoặc lip-sync.
- Dựa vào **người thật**: ngoại hình, nhảy, người nổi tiếng, KOL cụ thể.
- Cần **chữ trên hình** để hiểu.
- Là **quảng cáo** hoặc nội dung tài trợ.
- Là **tin xã hội nhạy cảm**: tai nạn, ngộ độc, bạo lực, scandal cá nhân.
- Chế giễu ngoại hình, nhóm người, hoặc chỉ sao chép một video cụ thể.

Giữ lại trend có **lõi hành vi**: một tình huống, cảm xúc hoặc thói quen có thể diễn bằng cơ thể.

### Bước 0.3: Phân tích vì sao viral

Với mỗi trend còn lại, ghi 5 dòng:

| Trường | Câu hỏi | Ví dụ "Hội Chó Xấu" |
|---|---|---|
| Lõi cảm xúc | Người xem thấy gì trong đó? | Thương cái không hoàn hảo |
| Tình huống gốc | Hành vi lặp lại trong các video là gì? | Chủ cố chụp ảnh đẹp, thú cưng góc nào cũng "dìm" |
| Cơ chế lan | Vì sao người ta share/comment? | Khoe thú cưng của mình ở bình luận |
| Phần mượn | Lấy gì cho phim không lời? | Cảnh chủ chụp ảnh thú cưng thất bại liên tục |
| Hạn dùng | Trend còn sống bao lâu? | 1–2 tuần |

### Bước 0.4: Chấm điểm và chọn

Chấm mỗi ý tưởng trên thang 0–2 cho từng tiêu chí, tối đa 12 điểm:

| Tiêu chí | 0 | 1 | 2 |
|---|---|---|---|
| Độ nóng trend | Không còn ai nhắc | Có trong bài tổng hợp tuần | Có trong top 24h hoặc đúng dịp lễ |
| Diễn được không lời | Cần chữ hoặc nhạc | Cần giải thích một chút | Hiểu ngay bằng hành động |
| Nhận ra trong 2 giây | Không | Mơ hồ | Có |
| Có người để tag | Không | Chung chung | Gọi được một kiểu người cụ thể |
| Có phe để cãi | Không | Yếu | Rõ hai phe |
| Đáng xem lại | Không | Có chi tiết nhỏ | Cú kết đổi nghĩa frame đầu |

Ngưỡng chọn: **từ 8 điểm**. Ưu tiên trend có hạn dùng ngắn nếu kịp sản xuất. Kiểm tra tiếp **Dấu tập** cũ như hiện nay để không lặp.

### Bước 0.5: Ghi lại

Mỗi tập có thêm **TRENDS.md** trong thư mục tập, gồm: ngày quét, link nguồn, danh sách trend thô, trend bị loại kèm lý do, bảng phân tích, bảng điểm và lựa chọn cuối. FLOW.md thêm một dòng **Trend gốc** ngay dưới Dấu tập.

## 4. Áp phân tích vào kịch bản

- **Mở**: frame đầu tái hiện tình huống gốc của trend để người xem nhận ra ngay.
- **Giữa**: dùng đúng hành vi lặp lại mà người xem đã quen, nhưng đặt vào nhân vật của series.
- **Kết**: lật một chi tiết mà video trend gốc không có. Đây là phần khiến tập khác bản gốc và đáng xem lại.
- **Gói đăng bài**: caption và hashtag gọi đúng trend, ví dụ `#chođấu` hay `#2020`. Bình luận ghim mời người xem khoe phiên bản của họ, đúng cơ chế lan đã phân tích.

## 5. Có cần "loop" tự chạy không?

Không ở giai đoạn đầu. Lý do:

- Mỗi lần gọi `$dao-dien-tap` đã quét trend tươi, nên dữ liệu luôn mới đúng lúc cần.
- Loop chạy định kỳ tốn token kể cả những ngày không làm video.
- Trend Việt đổi theo tuần, không theo giờ.

Khi nào bật loop: khi làm từ 3 tập/tuần trở lên và muốn có sẵn danh sách ý tưởng. Lúc đó dùng `/loop 1d` hoặc lịch cron gọi riêng bước 0, ghi vào `../stickman-video-projects/doi-thuong/_trends/YYYY-MM-DD.md`. Skill đọc file mới nhất nếu chưa quá 48 giờ, nếu cũ hơn thì quét lại.

## 6. Lộ trình

| Giai đoạn | Việc | File đổi | Kiểm tra |
|---|---|---|---|
| 1 | Thêm bước 0 vào `SKILL.md`, thêm mục TRENDS.md và dòng Trend gốc vào gói bàn giao | `skills/dao-dien-tap/SKILL.md` | Gọi `$dao-dien-tap` trống một lần, xem TRENDS.md có link nguồn thật và bảng điểm |
| 2 | Bật loop quét hằng ngày nếu tần suất làm video đủ cao | Không đổi skill, chỉ thêm lịch | Thư mục `_trends/` có file mới mỗi ngày |
| 3 | Ghi số liệu sau đăng: view, share, comment sau 48 giờ vào FLOW.md để biết loại trend nào hợp kênh | `SKILL.md` thêm một mục | Sau 5 tập, so điểm chấm với kết quả thật |

## 7. Rủi ro

- **Nguồn đổi giao diện hoặc chặn crawl.** Endless và báo có thể đổi bất cứ lúc nào. Có phương án lùi về danh sách chủ đề sẵn có.
- **Trend hết hạn trước khi đăng.** Một tập mất 1–3 ngày sản xuất. Trend dịp lễ phải chọn trước ít nhất 3 ngày.
- **Bản quyền và sao chép.** Chỉ mượn tình huống, không mượn nhạc, hình hay kịch bản của video cụ thể.
- **Nội dung nhạy cảm lọt lưới.** Bộ lọc ở bước 0.2 là bắt buộc, không phải gợi ý.
