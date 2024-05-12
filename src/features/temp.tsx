import { client } from "@/utils/trpc";

export default () => {
  const handler = async () => {
    let cooks: { [key: string]: string };
    const response = await client.deicms.loginProcedureStart
      .query({ username: "2201854", password: "14112003" })
      .then((response) => {
        cooks = response.cookies;
        console.log(response);
        return client.deicms.getLoginDetails.query({
          username: "2201854",
          password: "14112003",
          cookies: response.cookies,
          userGroupId: response.data.loginInfo.loginInfo.userGroupId,
        });
      })
      .then((data) => console.log(data));
  };
  return (
    <>
      <h1>testing</h1>
      <button onClick={handler}>chsdi</button>
      <button
        onClick={async () => {
          const r1 = await client.deicms.login.query({ username: "2201854", password: "14112003" });
          const r2 = await client.deicms.getStudentRollNumber.query();
          const r3 = await client.deicms.getRegisteredSemesterCourseList.query(4);
          const r4 = await client.deicms.getStudentMarks.query("MEM402");
          console.log(r4);
        }}
      >
        maginv
      </button>
      <button class="btn btn-wide">Wide</button>
      <label class="form-control w-full max-w-xs">
        <div class="label">
          <span class="label-text">What is your name?</span>
          <span class="label-text-alt">Top Right label</span>
        </div>
        <input type="text" placeholder="Type here" class="input input-bordered w-full max-w-xs" />
        <div class="label">
          <span class="label-text-alt">Bottom Left label</span>
          <span class="label-text-alt">Bottom Right label</span>
        </div>
      </label>
    </>
  );
};
