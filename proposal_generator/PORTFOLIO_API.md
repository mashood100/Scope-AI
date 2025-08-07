# Portfolio Management API

A comprehensive portfolio management system with AI-powered tag generation, technology extraction, and vector embeddings for intelligent project matching.

## 🚀 Features

- **AI-Powered Analysis**: Automatic tag generation, technology extraction, and project categorization
- **Vector Embeddings**: Semantic similarity matching between projects and job descriptions
- **Smart Metadata**: AI-generated summaries, complexity assessment, and project type classification
- **Full CRUD Operations**: Create, read, update, and delete portfolio projects
- **Similarity Search**: Find relevant projects based on job descriptions

## 📊 AI Analysis Capabilities

When you create a portfolio project, the AI automatically analyzes and extracts:

- **Tags**: 5-8 relevant keywords (e.g., "e-commerce", "real-time", "responsive")
- **Technologies**: Specific frameworks, languages, and tools used
- **Project Type**: web_app, mobile_app, api, desktop_app, game, ai_ml, or other
- **Complexity Level**: beginner, intermediate, advanced, or expert
- **AI Summary**: Professional 2-3 sentence project description
- **Vector Embeddings**: 1536-dimensional vectors for similarity matching

## 🔗 API Endpoints

### 1. Create Portfolio Project

**POST** `/proposals/api/portfolio/create/`

Create a new portfolio project with AI analysis.

**Request Body:**

```json
{
  "name": "E-commerce Mobile App",
  "description": "A full-featured Flutter e-commerce app with Firebase backend, Stripe payments, real-time chat support, and advanced product filtering. Built with clean architecture and state management using Riverpod.",
  "user_id": "user123",
  "github_url": "https://github.com/user/ecommerce-app",
  "live_url": "https://myapp.com",
  "app_store_url": "https://apps.apple.com/app/myapp",
  "images": [
    "https://example.com/image1.jpg",
    "https://example.com/image2.jpg"
  ],
  "is_featured": true
}
```

**Response:**

```json
{
  "success": true,
  "project_id": 1,
  "name": "E-commerce Mobile App",
  "ai_summary": "A comprehensive Flutter e-commerce application featuring Firebase integration, Stripe payment processing, and real-time chat functionality with clean architecture implementation.",
  "tags": [
    "e-commerce",
    "mobile-app",
    "real-time",
    "payments",
    "flutter",
    "firebase",
    "chat"
  ],
  "technologies": ["Flutter", "Dart", "Firebase", "Stripe", "Riverpod"],
  "project_type": "mobile_app",
  "complexity_level": "advanced",
  "created_at": "2024-01-15T10:30:00Z",
  "message": "Portfolio project created successfully"
}
```

### 2. Get User Portfolio

**GET** `/proposals/api/portfolio/user/{user_id}/`

Retrieve all portfolio projects for a user with optional filtering.

**Query Parameters:**

- `project_type`: Filter by project type (web_app, mobile_app, etc.)
- `is_featured`: Filter featured projects (true/false)
- `page`: Page number for pagination

**Example:** `/proposals/api/portfolio/user/user123/?project_type=mobile_app&is_featured=true`

**Response:**

```json
{
  "count": 15,
  "next": "http://localhost:8000/proposals/api/portfolio/user/user123/?page=2",
  "previous": null,
  "results": [
    {
      "id": 1,
      "name": "E-commerce Mobile App",
      "description": "A full-featured Flutter e-commerce app with Firebase...",
      "ai_summary": "A comprehensive Flutter e-commerce application...",
      "tags": ["e-commerce", "mobile-app", "real-time"],
      "technologies": ["Flutter", "Dart", "Firebase"],
      "project_type": "mobile_app",
      "complexity_level": "advanced",
      "github_url": "https://github.com/user/ecommerce-app",
      "live_url": "https://myapp.com",
      "app_store_url": "https://apps.apple.com/app/myapp",
      "images": ["https://example.com/image1.jpg"],
      "is_featured": true,
      "created_at": "2024-01-15T10:30:00Z",
      "updated_at": "2024-01-15T10:30:00Z"
    }
  ]
}
```

### 3. Get Portfolio Project Details

**GET** `/proposals/api/portfolio/detail/{project_id}/`

Get detailed information about a specific project.

**Response:**

```json
{
  "id": 1,
  "name": "E-commerce Mobile App",
  "description": "Full project description...",
  "user_id": "user123",
  "tags": ["e-commerce", "mobile-app", "real-time"],
  "ai_summary": "A comprehensive Flutter e-commerce application...",
  "technologies": ["Flutter", "Dart", "Firebase", "Stripe"],
  "project_type": "mobile_app",
  "complexity_level": "advanced",
  "github_url": "https://github.com/user/ecommerce-app",
  "live_url": "https://myapp.com",
  "app_store_url": "https://apps.apple.com/app/myapp",
  "images": ["https://example.com/image1.jpg"],
  "is_featured": true,
  "created_at": "2024-01-15T10:30:00Z",
  "updated_at": "2024-01-15T10:30:00Z",
  "embedding_dimensions": 1536
}
```

### 4. Update Portfolio Project

**PUT** `/proposals/api/portfolio/detail/{project_id}/`

Update a portfolio project. If description changes, AI re-analysis is triggered.

**Request Body:** (Same as create, all fields optional)

```json
{
  "name": "Updated Project Name",
  "description": "Updated description triggers AI re-analysis",
  "is_featured": false
}
```

### 5. Delete Portfolio Project

**DELETE** `/proposals/api/portfolio/detail/{project_id}/`

Delete a portfolio project.

**Response:**

```json
{
  "success": true,
  "message": "Portfolio project 'E-commerce Mobile App' deleted successfully"
}
```

### 6. Find Similar Projects

**POST** `/proposals/api/portfolio/similar/`

Find portfolio projects most similar to a job description using vector embeddings.

**Request Body:**

```json
{
  "job_description": "I need a Flutter developer to build an e-commerce mobile app with payment integration and real-time features",
  "user_id": "user123",
  "top_k": 3
}
```

**Response:**

```json
{
  "similar_projects": [
    {
      "project_id": 1,
      "name": "E-commerce Mobile App",
      "ai_summary": "A comprehensive Flutter e-commerce application...",
      "tags": ["e-commerce", "mobile-app", "real-time", "payments"],
      "technologies": ["Flutter", "Dart", "Firebase", "Stripe"],
      "project_type": "mobile_app",
      "complexity_level": "advanced",
      "github_url": "https://github.com/user/ecommerce-app",
      "live_url": "https://myapp.com",
      "app_store_url": "https://apps.apple.com/app/myapp",
      "is_featured": true,
      "similarity_score": 0.8934
    },
    {
      "project_id": 5,
      "name": "Payment Processing API",
      "ai_summary": "RESTful API for payment processing...",
      "tags": ["api", "payments", "stripe", "backend"],
      "technologies": ["Node.js", "Express", "Stripe", "MongoDB"],
      "project_type": "api",
      "complexity_level": "intermediate",
      "github_url": "https://github.com/user/payment-api",
      "similarity_score": 0.7245
    }
  ],
  "total_found": 2,
  "job_description": "I need a Flutter developer to build an e-commerce mobile app with payment..."
}
```

## 🧠 AI Integration Details

### Technology Extraction

The AI analyzes project descriptions to identify:

- Programming languages (Python, JavaScript, Dart, etc.)
- Frameworks (React, Flutter, Django, etc.)
- Databases (MongoDB, PostgreSQL, Firebase, etc.)
- Cloud services (AWS, Google Cloud, etc.)
- Tools and libraries (Stripe, Socket.io, etc.)

### Vector Embeddings

- Uses OpenAI's `text-embedding-ada-002` model
- Generates 1536-dimensional vectors
- Enables semantic similarity search
- Cosine similarity calculation for matching

### Smart Categorization

Projects are automatically categorized into:

- **web_app**: Web applications and websites
- **mobile_app**: iOS, Android, and cross-platform apps
- **api**: Backend APIs and microservices
- **desktop_app**: Desktop applications
- **game**: Game development projects
- **ai_ml**: AI/ML and data science projects
- **other**: Miscellaneous projects

## 🔄 Integration with Proposal Generation

The portfolio system is designed to enhance proposal generation:

1. **Project Matching**: Use `/similar/` endpoint to find relevant projects
2. **Portfolio Integration**: Include matching projects in proposals
3. **Tailored Proposals**: Generate proposals based on similar past work
4. **Evidence-Based Bidding**: Reference specific projects in proposals

## 📝 Usage Examples

### Creating a Flutter Project

```bash
curl -X POST http://localhost:8000/proposals/api/portfolio/create/ \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Food Delivery App",
    "description": "Cross-platform Flutter app for food delivery with GPS tracking, real-time order updates, payment integration via Stripe, and push notifications. Uses Firebase for backend and GetX for state management.",
    "user_id": "freelancer123",
    "github_url": "https://github.com/user/food-delivery",
    "app_store_url": "https://apps.apple.com/app/food-delivery"
  }'
```

### Finding Similar Projects

```bash
curl -X POST http://localhost:8000/proposals/api/portfolio/similar/ \
  -H "Content-Type: application/json" \
  -d '{
    "job_description": "Need a mobile app developer for a restaurant ordering system with real-time tracking",
    "user_id": "freelancer123",
    "top_k": 2
  }'
```

### Getting User Portfolio

```bash
# All projects
curl http://localhost:8000/proposals/api/portfolio/user/freelancer123/

# Only mobile apps
curl "http://localhost:8000/proposals/api/portfolio/user/freelancer123/?project_type=mobile_app"

# Only featured projects
curl "http://localhost:8000/proposals/api/portfolio/user/freelancer123/?is_featured=true"
```

## 🛠️ Technical Requirements

1. **OpenAI API Key**: Required for AI analysis and embeddings
2. **Database**: PostgreSQL recommended for JSONField support
3. **Memory**: Vector embeddings require adequate memory for similarity calculations
4. **Processing Time**: Initial project creation takes 5-10 seconds due to AI analysis

## 🚦 Error Handling

All endpoints include comprehensive error handling:

- **400 Bad Request**: Missing required fields or validation errors
- **404 Not Found**: Project not found
- **500 Internal Server Error**: AI service failures or database errors

Example error response:

```json
{
  "error": "Project description must be at least 50 characters long"
}
```

## 🎯 Future Enhancements

- **Batch Processing**: Analyze multiple projects simultaneously
- **Custom Training**: Fine-tune embeddings for specific domains
- **Advanced Filtering**: Search by tags, technologies, or complexity
- **Analytics**: Track project performance and similarity trends
- **Export Features**: Generate portfolio PDFs or presentations
