import React, { useState } from 'react';
import { 
  FloatButton, 
  Modal, 
  Tooltip 
} from 'antd';
import { 
  RobotOutlined, 
  MessageOutlined, 
  AudioOutlined,
  CloseOutlined
} from '@ant-design/icons';
import AIChat from './AIChat';

const FloatingChatBot = () => {
  const [isModalVisible, setIsModalVisible] = useState(false);

  const showModal = () => {
    setIsModalVisible(true);
  };

  const handleCancel = () => {
    setIsModalVisible(false);
  };

  return (
    <>
      <FloatButton.Group
        trigger="hover"
        type="primary"
        style={{ 
          right: 24,
          bottom: 24,
        }}
        icon={<RobotOutlined />}
        tooltip="Nuwa AI助手"
      >
        <Tooltip title="AI对话" placement="left">
          <FloatButton
            icon={<MessageOutlined />}
            onClick={() => showModal()}
            style={{
              background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
              border: 'none'
            }}
          />
        </Tooltip>
        
        <Tooltip title="语音助手" placement="left">
          <FloatButton
            icon={<AudioOutlined />}
            onClick={() => showModal()}
            style={{
              background: 'linear-gradient(135deg, #52c41a 0%, #73d13d 100%)',
              border: 'none'
            }}
          />
        </Tooltip>
      </FloatButton.Group>

      <Modal
        title={null}
        open={isModalVisible}
        onCancel={handleCancel}
        footer={null}
        width="90vw"
        style={{ 
          top: 20,
          maxWidth: '1000px'
        }}
        styles={{
          content: {
            padding: '0',
            background: 'rgba(15, 23, 42, 0.98)',
            backdropFilter: 'blur(20px)',
            borderRadius: '16px',
            border: '1px solid rgba(255, 255, 255, 0.1)',
            boxShadow: '0 25px 80px rgba(0, 0, 0, 0.4)',
            overflow: 'hidden'
          },
          body: {
            padding: '0',
            height: '75vh',
            overflow: 'hidden'
          }
        }}
        closeIcon={
          <CloseOutlined style={{ 
            color: 'white', 
            fontSize: '16px',
            padding: '4px'
          }} />
        }
        centered
        destroyOnHidden
      >
        <AIChat />
      </Modal>
    </>
  );
};

export default FloatingChatBot;