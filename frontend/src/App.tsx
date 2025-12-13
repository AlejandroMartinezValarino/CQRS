import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { ConfigProvider } from 'antd';
import { ApolloProvider } from '@apollo/client';
import { Layout, Menu } from 'antd';
import { DashboardOutlined, UnorderedListOutlined, InteractionOutlined } from '@ant-design/icons';
import { apolloClient } from '@/services/graphql/client';
import { Dashboard } from '@/pages/Dashboard';
import { AnimeList } from '@/pages/AnimeList';
import { AnimeDetail } from '@/pages/AnimeDetail';
import { Interactions } from '@/pages/Interactions';
import { useNavigate, useLocation } from 'react-router-dom';

const { Header, Content, Sider } = Layout;

const AppLayout = () => {
  const navigate = useNavigate();
  const location = useLocation();

  const menuItems = [
    {
      key: '/animes',
      icon: <UnorderedListOutlined />,
      label: 'Explorar Animes',
    },
    {
      key: '/dashboard',
      icon: <DashboardOutlined />,
      label: 'Estadísticas',
    },
    {
      key: '/interactions',
      icon: <InteractionOutlined />,
      label: 'Interacciones',
    },
  ];

  return (
    <Layout style={{ minHeight: '100vh' }}>
      <Sider collapsible>
        <div style={{ height: '32px', margin: '16px', background: 'rgba(255, 255, 255, 0.3)' }} />
        <Menu
          theme="dark"
          mode="inline"
          selectedKeys={[location.pathname]}
          items={menuItems}
          onClick={({ key }) => navigate(key)}
        />
      </Sider>
      <Layout>
        <Header style={{ padding: '0 24px', background: '#fff' }}>
          <h1 style={{ margin: 0 }}>CQRS Anime Analytics</h1>
        </Header>
        <Content style={{ margin: '24px 16px', padding: 24, background: '#fff', minHeight: 280 }}>
          <Routes>
            <Route path="/animes" element={<AnimeList />} />
            <Route path="/animes/:id" element={<AnimeDetail />} />
            <Route path="/dashboard" element={<Dashboard />} />
            <Route path="/interactions" element={<Interactions />} />
            <Route path="/" element={<Navigate to="/animes" replace />} />
          </Routes>
        </Content>
      </Layout>
    </Layout>
  );
};

function App() {
  return (
    <ConfigProvider>
      <ApolloProvider client={apolloClient}>
        <BrowserRouter>
          <AppLayout />
        </BrowserRouter>
      </ApolloProvider>
    </ConfigProvider>
  );
}

export default App;
