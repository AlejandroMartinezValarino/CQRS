import { Spin } from 'antd';

export const Loading = () => {
  return (
    <div style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', minHeight: '200px' }}>
      <Spin size="large" />
    </div>
  );
};
