import Login from '@/views/login/index.vue'
import Home from '@/views/home/index.vue'
import Dashboard from '@/views/dashboard/index.vue'

const routes = [
  {
    path: '/',
    name: 'Home',
    component: Home,
    meta: { requireAuth: true },
    redirect: '/dashboard',
    children: [
      {
        path: '/dashboard',
        name: 'Dashboard',
        component: Dashboard,
        meta: { title: '仪表盘', icon: 'DataLine' }
      },
      {
        path: '/children',
        name: 'Children',
        redirect: '/children/index',
        meta: { title: '幼儿管理', icon: 'Avatar' },
        children: [
          {
            path: 'index',
            name: 'ChildrenIndex',
            component: () => import('@/views/children/index.vue'),
            meta: { title: '幼儿列表', icon: 'Grid' }
          }
        ]
      },
      {
        path: '/classes',
        name: 'Classes',
        redirect: '/classes/index',
        meta: { title: '班级管理', icon: 'School' },
        children: [
          {
            path: 'index',
            name: 'ClassesIndex',
            component: () => import('@/views/classes/index.vue'),
            meta: { title: '班级列表', icon: 'Grid' }
          }
        ]
      },
      {
        path: '/teachers',
        name: 'Teachers',
        redirect: '/teachers/index',
        meta: { title: '教师管理', icon: 'User' },
        children: [
          {
            path: 'index',
            name: 'TeachersIndex',
            component: () => import('@/views/teachers/index.vue'),
            meta: { title: '教师列表', icon: 'Grid' }
          }
        ]
      },
      {
        path: '/selections',
        name: 'Selections',
        redirect: '/selections/index',
        meta: { title: '选区管理', icon: 'MapLocation' },
        children: [
          {
            path: 'index',
            name: 'SelectionList',
            component: () => import('@/views/selections/index.vue'),
            meta: { title: '选区列表', icon: 'Location' }
          },
          {
            path: 'records',
            name: 'SelectionRecords',
            component: () => import('@/views/selections/records.vue'),
            meta: { title: '选区记录', icon: 'Document' }
          },
          {
            path: 'operation',
            name: 'SelectionOperation',
            component: () => import('@/views/selections/selection-operation.vue'),
            meta: { title: '幼儿选区操作', icon: 'Position' }
          }
        ]
      },
      {
        path: '/system',
        name: 'System',
        redirect: '/system/kindergarten',
        meta: { title: '系统管理', icon: 'Setting' },
        children: [
          {
            path: 'kindergarten',
            name: 'KindergartenList',
            component: () => import('@/views/kindergarten/index.vue'),
            meta: { title: '幼儿园列表', icon: 'OfficeBuilding' }
          },
          {
            path: 'users',
            name: 'UserList',
            component: () => import('@/views/system/users.vue'),
            meta: { title: '用户管理', icon: 'User' }
          }
        ]
      }
    ]
  },
  {
    path: '/login',
    name: 'Login',
    component: Login,
    meta: { requireAuth: false }
  }
]

export default routes