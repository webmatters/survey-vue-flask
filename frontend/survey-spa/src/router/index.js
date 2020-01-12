import Vue from "vue";
import VueRouter from "vue-router";
import Home from "../views/Home.vue";
import store from "@/store";

Vue.use(VueRouter);

const routes = [
  {
    path: "/",
    name: "home",
    component: Home
  },
  {
    path: "/surveys/:id",
    name: "survey",

    component: () => import("../views/Survey.vue")
  },
  {
    path: "/surveys",
    name: "NewSurvey",

    component: () => import("../views/NewSurvey.vue"),
    beforeEnter(to, from, next) {
      if (!store.getters.isAuthenticated) {
        next("/login");
      } else {
        next();
      }
    }
  },
  {
    path: "/login",
    name: "Login",

    component: () => import("../components/Login.vue")
  }
];

const router = new VueRouter({
  routes
});

export default router;
