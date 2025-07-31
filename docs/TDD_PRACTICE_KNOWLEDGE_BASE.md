# TDD实践知识库

## 🎯 **知识库概览**

本知识库为Digital Employees Agent系统提供全面的TDD实践指导，涵盖各技术栈的最佳实践、代码模板和实施方案。

## 📋 **技术栈覆盖范围**

基于我们优化的6个TDD核心agent的技术栈：

| Agent | 技术栈 | TDD重点 |
|-------|--------|---------|
| **qa-engineer** | 测试框架、CI/CD | TDD教练和质量门禁 |
| **senior-rd-engineer** | 架构设计、方法论 | TDD方法论和技术指导 |
| **backend-pro** | Node.js, Python, Java, Go | API和服务端TDD |
| **fullstack-developer** | React, Vue, React Native | 前端组件TDD |
| **ai-ml-engineer** | Python, TensorFlow, PyTorch | ML模型和数据管道TDD |

---

## 🌐 **Backend TDD实践**

### **Node.js + Express API TDD**

#### **测试环境配置**
```javascript
// package.json
{
  "devDependencies": {
    "jest": "^29.0.0",
    "supertest": "^6.0.0",
    "@types/jest": "^29.0.0",
    "ts-jest": "^29.0.0"
  },
  "scripts": {
    "test": "jest",
    "test:watch": "jest --watch",
    "test:coverage": "jest --coverage"
  }
}

// jest.config.js
module.exports = {
  preset: 'ts-jest',
  testEnvironment: 'node',
  coverageThreshold: {
    global: {
      branches: 90,
      functions: 90,
      lines: 90,
      statements: 90
    }
  }
};
```

#### **API端点TDD模板**
```javascript
// tests/api/users.test.js
describe('Users API', () => {
  describe('POST /api/users', () => {
    it('should create a new user with valid data', async () => {
      // Red: 写失败的测试
      const userData = {
        name: 'John Doe',
        email: 'john@example.com'
      };
      
      const response = await request(app)
        .post('/api/users')
        .send(userData)
        .expect(201);
      
      expect(response.body).toMatchObject({
        id: expect.any(String),
        name: userData.name,
        email: userData.email,
        createdAt: expect.any(String)
      });
    });
    
    it('should return 400 for invalid email', async () => {
      const invalidData = {
        name: 'John Doe',
        email: 'invalid-email'
      };
      
      await request(app)
        .post('/api/users')
        .send(invalidData)
        .expect(400);
    });
  });
});

// src/routes/users.js - Green: 最小实现
app.post('/api/users', async (req, res) => {
  const { name, email } = req.body;
  
  // 基本验证
  if (!isValidEmail(email)) {
    return res.status(400).json({ error: 'Invalid email' });
  }
  
  // 创建用户
  const user = await User.create({ name, email });
  res.status(201).json(user);
});
```

### **Python + FastAPI TDD**

#### **测试环境配置**
```python
# requirements-dev.txt
pytest==7.0.0
pytest-asyncio==0.20.0
httpx==0.24.0
pytest-cov==4.0.0

# pyproject.toml
[tool.pytest.ini_options]
testpaths = ["tests"]
asyncio_mode = "auto"
addopts = "--cov=src --cov-report=html --cov-fail-under=90"
```

#### **API端点TDD模板**
```python
# tests/test_users.py
import pytest
from httpx import AsyncClient
from main import app

@pytest.mark.asyncio
async def test_create_user_success():
    """Red: 测试创建用户成功场景"""
    async with AsyncClient(app=app, base_url="http://test") as client:
        user_data = {
            "name": "John Doe",
            "email": "john@example.com"
        }
        
        response = await client.post("/api/users", json=user_data)
        
        assert response.status_code == 201
        assert response.json()["name"] == user_data["name"]
        assert response.json()["email"] == user_data["email"]
        assert "id" in response.json()

@pytest.mark.asyncio
async def test_create_user_invalid_email():
    """Red: 测试无效邮箱场景"""
    async with AsyncClient(app=app, base_url="http://test") as client:
        user_data = {
            "name": "John Doe", 
            "email": "invalid-email"
        }
        
        response = await client.post("/api/users", json=user_data)
        assert response.status_code == 400

# main.py - Green: 最小实现
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, EmailStr

app = FastAPI()

class UserCreate(BaseModel):
    name: str
    email: EmailStr

@app.post("/api/users", status_code=201)
async def create_user(user: UserCreate):
    # 简单的用户创建逻辑
    user_dict = user.dict()
    user_dict["id"] = generate_id()
    return user_dict
```

---

## ⚛️ **Frontend TDD实践**

### **React Component TDD**

#### **测试环境配置**
```javascript
// package.json
{
  "devDependencies": {
    "@testing-library/react": "^13.0.0",
    "@testing-library/jest-dom": "^5.0.0",
    "@testing-library/user-event": "^14.0.0",
    "jest-environment-jsdom": "^29.0.0"
  }
}

// jest.config.js
module.exports = {
  testEnvironment: 'jsdom',
  setupFilesAfterEnv: ['<rootDir>/src/setupTests.js'],
  moduleNameMapping: {
    '\\.(css|less|scss)$': 'identity-obj-proxy'
  }
};
```

#### **React组件TDD模板**
```javascript
// tests/components/UserForm.test.jsx
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import UserForm from '../UserForm';

describe('UserForm', () => {
  it('should render form fields', () => {
    // Red: 测试组件渲染
    render(<UserForm onSubmit={jest.fn()} />);
    
    expect(screen.getByLabelText(/name/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/email/i)).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /submit/i })).toBeInTheDocument();
  });
  
  it('should call onSubmit with form data', async () => {
    // Red: 测试表单提交
    const mockOnSubmit = jest.fn();
    const user = userEvent.setup();
    
    render(<UserForm onSubmit={mockOnSubmit} />);
    
    await user.type(screen.getByLabelText(/name/i), 'John Doe');
    await user.type(screen.getByLabelText(/email/i), 'john@example.com');
    await user.click(screen.getByRole('button', { name: /submit/i }));
    
    await waitFor(() => {
      expect(mockOnSubmit).toHaveBeenCalledWith({
        name: 'John Doe',
        email: 'john@example.com'
      });
    });
  });
  
  it('should show validation error for invalid email', async () => {
    // Red: 测试表单验证
    const user = userEvent.setup();
    
    render(<UserForm onSubmit={jest.fn()} />);
    
    await user.type(screen.getByLabelText(/email/i), 'invalid-email');
    await user.click(screen.getByRole('button', { name: /submit/i }));
    
    expect(screen.getByText(/invalid email/i)).toBeInTheDocument();
  });
});

// src/components/UserForm.jsx - Green: 最小实现
import { useState } from 'react';

const UserForm = ({ onSubmit }) => {
  const [formData, setFormData] = useState({ name: '', email: '' });
  const [errors, setErrors] = useState({});
  
  const validateEmail = (email) => {
    return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email);
  };
  
  const handleSubmit = (e) => {
    e.preventDefault();
    
    const newErrors = {};
    if (!validateEmail(formData.email)) {
      newErrors.email = 'Invalid email';
    }
    
    if (Object.keys(newErrors).length > 0) {
      setErrors(newErrors);
      return;
    }
    
    onSubmit(formData);
  };
  
  return (
    <form onSubmit={handleSubmit}>
      <label>
        Name:
        <input
          type="text"
          value={formData.name}
          onChange={(e) => setFormData({...formData, name: e.target.value})}
        />
      </label>
      
      <label>
        Email:
        <input
          type="email"
          value={formData.email}
          onChange={(e) => setFormData({...formData, email: e.target.value})}
        />
      </label>
      {errors.email && <span>{errors.email}</span>}
      
      <button type="submit">Submit</button>
    </form>
  );
};

export default UserForm;
```

### **Vue Component TDD**

#### **Vue组件TDD模板**
```javascript
// tests/components/UserForm.spec.js
import { mount } from '@vue/test-utils';
import UserForm from '@/components/UserForm.vue';

describe('UserForm.vue', () => {
  it('renders form fields', () => {
    // Red: 测试组件渲染
    const wrapper = mount(UserForm);
    
    expect(wrapper.find('input[data-testid="name"]').exists()).toBe(true);
    expect(wrapper.find('input[data-testid="email"]').exists()).toBe(true);
    expect(wrapper.find('button[type="submit"]').exists()).toBe(true);
  });
  
  it('emits submit event with form data', async () => {
    // Red: 测试表单提交
    const wrapper = mount(UserForm);
    
    await wrapper.find('input[data-testid="name"]').setValue('John Doe');
    await wrapper.find('input[data-testid="email"]').setValue('john@example.com');
    await wrapper.find('form').trigger('submit.prevent');
    
    expect(wrapper.emitted('submit')).toBeTruthy();
    expect(wrapper.emitted('submit')[0]).toEqual([{
      name: 'John Doe',
      email: 'john@example.com'
    }]);
  });
});
```

---

## 🤖 **AI/ML TDD实践**

### **数据管道TDD**

#### **数据处理TDD模板**
```python
# tests/test_data_pipeline.py
import pytest
import pandas as pd
from src.data_pipeline import DataProcessor

class TestDataProcessor:
    
    def test_clean_data_removes_nulls(self):
        """Red: 测试数据清洗功能"""
        # 准备测试数据
        dirty_data = pd.DataFrame({
            'name': ['Alice', None, 'Bob'],
            'age': [25, 30, None],
            'email': ['alice@test.com', 'bob@test.com', 'charlie@test.com']
        })
        
        processor = DataProcessor()
        clean_data = processor.clean_data(dirty_data)
        
        # 验证清洗结果
        assert clean_data.isnull().sum().sum() == 0
        assert len(clean_data) == 1  # 只有完整的行被保留
        assert clean_data.iloc[0]['name'] == 'Alice'
    
    def test_feature_engineering_creates_age_groups(self):
        """Red: 测试特征工程"""
        input_data = pd.DataFrame({
            'name': ['Alice', 'Bob', 'Charlie'],
            'age': [22, 35, 45]
        })
        
        processor = DataProcessor()
        result = processor.create_age_groups(input_data)
        
        expected_groups = ['young', 'adult', 'senior']
        assert 'age_group' in result.columns
        assert list(result['age_group']) == expected_groups

# src/data_pipeline.py - Green: 最小实现
import pandas as pd

class DataProcessor:
    def clean_data(self, df):
        """移除包含空值的行"""
        return df.dropna()
    
    def create_age_groups(self, df):
        """创建年龄分组特征"""
        df = df.copy()
        df['age_group'] = df['age'].apply(lambda x: 
            'young' if x < 30 else 
            'adult' if x < 40 else 
            'senior'
        )
        return df
```

### **ML模型TDD**

#### **模型训练TDD模板**
```python
# tests/test_ml_model.py
import pytest
import numpy as np
from sklearn.datasets import make_classification
from src.ml_model import UserBehaviorClassifier

class TestUserBehaviorClassifier:
    
    @pytest.fixture
    def sample_data(self):
        """准备测试数据"""
        X, y = make_classification(
            n_samples=100, 
            n_features=4, 
            n_classes=2, 
            random_state=42
        )
        return X, y
    
    def test_model_training(self, sample_data):
        """Red: 测试模型训练"""
        X, y = sample_data
        
        classifier = UserBehaviorClassifier()
        classifier.train(X, y)
        
        # 验证模型已训练
        assert classifier.is_trained() == True
        assert classifier.model is not None
    
    def test_model_prediction(self, sample_data):
        """Red: 测试模型预测"""
        X, y = sample_data
        
        classifier = UserBehaviorClassifier()
        classifier.train(X, y)
        
        # 测试预测
        predictions = classifier.predict(X[:5])
        
        assert len(predictions) == 5
        assert all(pred in [0, 1] for pred in predictions)
    
    def test_model_accuracy_threshold(self, sample_data):
        """Red: 测试模型性能阈值"""
        X, y = sample_data
        
        classifier = UserBehaviorClassifier()
        classifier.train(X, y)
        
        accuracy = classifier.evaluate(X, y)
        
        # 模型准确率应该达到最低阈值
        assert accuracy >= 0.8

# src/ml_model.py - Green: 最小实现
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score

class UserBehaviorClassifier:
    def __init__(self):
        self.model = None
        self._trained = False
    
    def train(self, X, y):
        """训练模型"""
        self.model = RandomForestClassifier(random_state=42)
        self.model.fit(X, y)
        self._trained = True
    
    def predict(self, X):
        """预测"""
        if not self._trained:
            raise ValueError("Model must be trained first")
        return self.model.predict(X)
    
    def evaluate(self, X, y):
        """评估模型"""
        predictions = self.predict(X)
        return accuracy_score(y, predictions)
    
    def is_trained(self):
        """检查模型是否已训练"""
        return self._trained
```

---

## 📊 **TDD最佳实践指南**

### **通用TDD原则**

#### **1. Red-Green-Refactor循环**
```
🔴 Red: 写一个失败的测试
├── 编写最小的测试用例
├── 确保测试运行失败
└── 明确期望的行为

🟢 Green: 让测试通过
├── 编写最少的代码让测试通过
├── 不考虑代码优雅性
└── 专注于功能实现

🔵 Refactor: 重构代码
├── 改进代码结构和设计
├── 保持测试通过
└── 消除重复和改善可读性
```

#### **2. 测试命名规范**
```javascript
// 好的测试命名
describe('UserService', () => {
  describe('createUser', () => {
    it('should create user with valid data', () => {});
    it('should throw error when email is invalid', () => {});
    it('should throw error when email already exists', () => {});
  });
});

// 避免的测试命名
it('test user creation', () => {}); // 太模糊
it('should work', () => {}); // 没有具体描述
```

#### **3. 测试结构模式**
```javascript
// AAA模式 (Arrange-Act-Assert)
it('should calculate total price with tax', () => {
  // Arrange: 准备测试数据
  const cart = new ShoppingCart();
  cart.addItem({ price: 100, quantity: 2 });
  const taxRate = 0.1;
  
  // Act: 执行被测试的行为
  const total = cart.calculateTotal(taxRate);
  
  // Assert: 验证结果
  expect(total).toBe(220);
});
```

### **技术栈特定指南**

#### **Backend API TDD检查清单**
- ✅ 为每个HTTP端点编写测试
- ✅ 测试不同的HTTP状态码场景
- ✅ 验证请求/响应数据格式
- ✅ 测试认证和授权逻辑
- ✅ 测试错误处理和边界条件
- ✅ 使用测试数据库或Mock数据

#### **Frontend Component TDD检查清单**
- ✅ 测试组件渲染和Props传递
- ✅ 测试用户交互事件处理
- ✅ 测试组件状态变化
- ✅ 测试条件渲染逻辑
- ✅ 测试表单验证和提交
- ✅ Mock外部依赖和API调用

#### **AI/ML TDD检查清单**
- ✅ 测试数据预处理和清洗逻辑
- ✅ 测试特征工程函数
- ✅ 测试模型训练和预测流程
- ✅ 测试模型性能指标计算
- ✅ 测试数据管道的端到端流程
- ✅ 使用确定性的测试数据集

---

## 🛠️ **TDD工具链推荐**

### **通用工具**
- **版本控制**: Git + Git Hooks for pre-commit testing
- **CI/CD**: GitHub Actions, GitLab CI, Jenkins
- **代码覆盖率**: Codecov, SonarQube
- **质量门禁**: SonarQube, ESLint, Prettier

### **语言特定工具**

#### **JavaScript/TypeScript**
- **测试框架**: Jest, Vitest, Mocha
- **断言库**: Jest (内置), Chai
- **Mock库**: Jest (内置), Sinon
- **UI测试**: Testing Library, Cypress, Playwright

#### **Python** 
- **测试框架**: pytest, unittest
- **Mock库**: unittest.mock, pytest-mock
- **覆盖率**: pytest-cov, coverage.py
- **ML测试**: pytest-xdist (并行), great-expectations (数据质量)

#### **Java**
- **测试框架**: JUnit 5, TestNG
- **Mock库**: Mockito, PowerMock
- **断言库**: AssertJ, Hamcrest
- **集成测试**: TestContainers, WireMock

---

## 📈 **TDD度量和监控**

### **关键指标**
```yaml
TDD健康度量:
  过程指标:
    - 测试覆盖率: >90%
    - 测试通过率: >95%
    - 构建成功率: >90%
    - TDD循环完整性: >85%
  
  质量指标:
    - 生产缺陷率: 月度趋势
    - 代码重复率: <5%
    - 技术债务: SonarQube评分
    - 代码复杂度: 圈复杂度<10
  
  效率指标:
    - 功能交付速度: story/sprint
    - 缺陷修复时间: 平均小时数
    - 代码审查时间: 平均小时数
    - 部署频率: 次/周
```

### **监控仪表板模板**
```javascript
// TDD仪表板配置示例
const tddDashboard = {
  metrics: [
    {
      name: 'Test Coverage',
      target: 90,
      current: 92,
      trend: 'up'
    },
    {
      name: 'Build Success Rate', 
      target: 90,
      current: 88,
      trend: 'down'
    },
    {
      name: 'Defect Rate',
      target: '<2%',
      current: 1.5,
      trend: 'stable'
    }
  ],
  alerts: [
    'Coverage dropped below 90% in module X',
    'Build failing for 3 consecutive commits'
  ]
};
```

---

## 🎓 **TDD培训计划**

### **初级TDD培训（第1-2周）**
- TDD基础理论和红绿重构循环
- 单元测试编写实践
- Mock和Stub的使用
- 测试命名和组织

### **中级TDD培训（第3-4周）**
- 集成测试和契约测试
- TDD在不同架构中的应用
- 遗留代码的TDD重构策略
- 测试策略设计

### **高级TDD培训（第5-6周）**  
- TDD架构设计原则
- 复杂业务逻辑的TDD实践
- TDD与微服务架构
- TDD团队文化建设

### **专项TDD培训**
- **前端TDD**: React/Vue组件测试实践
- **后端TDD**: API和微服务测试策略
- **AI/ML TDD**: 数据科学项目的TDD方法

---

## 📚 **学习资源**

### **经典书籍**
- 《测试驱动开发：实战与模式解析》- Kent Beck
- 《重构：改善既有代码的设计》- Martin Fowler  
- 《代码整洁之道》- Robert C. Martin
- 《单元测试的艺术》- Roy Osherove

### **在线资源**
- [TDD官方文档](https://testdriven.io/)
- [Kent Beck TDD视频教程](https://www.youtube.com/playlist?list=PLlAML-kjpXX4lGcEppJwRh4g3BrKW7Ni6)
- [Martin Fowler博客TDD系列](https://martinfowler.com/tags/test%20driven%20development.html)

### **实践项目**
- [TDD Kata练习](https://codingdojo.org/kata/)
- [Exercism TDD练习题](https://exercism.org/)
- [TDD实践项目模板](https://github.com/testdouble/contributing-tests)

---

## 📝 **总结**

这个TDD实践知识库为Digital Employees Agent系统提供了：

✅ **全面的技术栈覆盖**: Backend、Frontend、AI/ML的TDD实践
✅ **实用的代码模板**: 即用的测试代码和实现模板
✅ **系统的最佳实践**: 经过验证的TDD方法论和规范
✅ **完善的工具链**: 各技术栈的工具推荐和配置
✅ **量化的度量体系**: TDD健康度量和监控方案
✅ **结构化的培训计划**: 从初级到高级的TDD技能发展路径

通过这个知识库，我们的agent系统能够为用户提供最专业的TDD指导和支持。