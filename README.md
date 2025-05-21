# DEHA_Rental
# Hướng dẫn cài đặt và chạy dự án Hotel Management

## Cấu trúc dự án

Dự án được chia thành 2 phần chính:

### 1. Client (Frontend)
- Sử dụng Next.js 15.3.1 với TypeScript
- Các công nghệ chính:
  - React 19
  - Redux Toolkit để quản lý state
  - TailwindCSS cho styling
  - AWS Amplify cho authentication
  - Mapbox GL cho hiển thị bản đồ
  - Radix UI cho các components

Cấu trúc thư mục client:
```
client/
├── src/
│   ├── app/                 # Next.js app router
│   ├── components/          # React components
│   ├── lib/                 # Utilities và schemas
│   └── state/              # Redux store và API
├── public/                  # Static files
└── package.json            # Dependencies
```

### 2. Server (Backend)
- Sử dụng Django (GeoDjango) cho backend
- Cấu trúc theo mô hình MVT (Model-View-Template)

## Hướng dẫn cài đặt

### 1. Frontend (Client)

```bash
cd Source/client
npm install
```

Tạo file .env với các biến môi trường cần thiết:
```plaintext
NEXT_PUBLIC_MAPBOX_TOKEN=your_mapbox_token
NEXT_PUBLIC_API_URL=http://localhost:8000
```

Chạy development server:
```bash
npm run dev
```

### 2. Backend (Server)

Yêu cầu:
- Python 3.x
- PostgreSQL với PostGIS extension

Các bước cài đặt:
```bash
cd Source/server
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

Thiết lập database và chạy migrations:
```bash
python manage.py migrate
python manage.py runserver
```

## Phân tích chức năng

### Frontend

1. **Authentication & Authorization**
- Sử dụng AWS Amplify cho xác thực người dùng
- Phân quyền: Manager và Tenant

2. **Routing & Layouts**
- Sử dụng Next.js App Router với 2 layout chính:
  - Dashboard layout (`(dashboard)/layout.tsx`): Cho người dùng đã đăng nhập
  - Non-dashboard layout (`(nondashboard)/layout.tsx`): Cho trang công khai

3. **Components chính**
- `AppSidebar.tsx`: Sidebar cho dashboard với các menu khác nhau cho Manager/Tenant
- `Listings.tsx`: Hiển thị danh sách bất động sản
- UI Components: Sử dụng Radix UI với custom styling

4. **State Management**
- Redux Toolkit cho global state
- RTK Query cho API calls

### Backend (GeoDjango)

1. **Core Module**
- Cấu hình cơ bản của Django
- Database settings
- URL routing

2. **Apps Module**
- Views: Xử lý business logic
- Models: Định nghĩa schema database
- Serializers: Chuyển đổi data

## Chức năng chính

1. **Cho Manager**
- Quản lý properties
- Xem và xử lý applications
- Quản lý settings

2. **Cho Tenant**
- Tìm kiếm và xem properties
- Thêm vào favorites
- Gửi applications
- Quản lý residences

3. **Chức năng chung**
- Authentication
- Profile management
- Search với filter
- Map view cho properties

        
