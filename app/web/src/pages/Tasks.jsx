import React, { useState } from 'react';
import { Card, Input, Button, Form, message, Typography, Divider } from 'antd';
import { PlusOutlined } from '@ant-design/icons';
import { createTask } from '../api/tasks';

const { TextArea } = Input;
const { Title, Text } = Typography;

const Tasks = () => {
  const [form] = Form.useForm();
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);

  const handleCreateTask = async (values) => {
    setLoading(true);
    try {
      const response = await createTask(values.userInput);
      setResult(response);
      message.success('任务创建成功！');
      form.resetFields();
    } catch (error) {
      console.error('创建任务失败:', error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div>
      <Title level={2}>任务管理</Title>
      
      <Card title="创建新任务" style={{ marginBottom: 24 }}>
        <Form
          form={form}
          layout="vertical"
          onFinish={handleCreateTask}
        >
          <Form.Item
            name="userInput"
            label="任务描述"
            rules={[{ required: true, message: '请输入任务描述' }]}
          >
            <TextArea
              rows={4}
              placeholder="请详细描述您要创建的任务..."
              showCount
              maxLength={500}
            />
          </Form.Item>
          
          <Form.Item>
            <Button 
              type="primary" 
              htmlType="submit" 
              loading={loading}
              icon={<PlusOutlined />}
            >
              创建任务
            </Button>
          </Form.Item>
        </Form>
      </Card>

      {result && (
        <Card title="任务创建结果">
          <Text code>{JSON.stringify(result, null, 2)}</Text>
        </Card>
      )}
    </div>
  );
};

export default Tasks;